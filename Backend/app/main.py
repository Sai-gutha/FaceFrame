from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import db, initialize_database
from .schemas import AuthResponse, CartItemRequest, CartQuantityRequest, LoginRequest, RegisterRequest
from .security import create_session_token, hash_password, hash_token, verify_password


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="FaceFrame API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


def public_frame(row) -> dict:
    return {
        "id": row["id"], "name": row["name"], "collection": row["collection_name"],
        "shape": row["shape"], "color": row["color"], "price_cents": row["price_cents"],
        "match_score": row["match_score"], "image_url": row["image_url"],
        "in_stock": row["inventory_count"] > 0,
    }


def current_user(authorization: Optional[str] = Header(default=None)) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    token = authorization.split(" ", 1)[1].strip()
    now = datetime.now(timezone.utc).isoformat()
    with db() as connection:
        row = connection.execute(
            """SELECT users.id, users.name, users.email
               FROM sessions JOIN users ON users.id = sessions.user_id
               WHERE sessions.token_hash = ? AND sessions.expires_at > ?""",
            (hash_token(token), now),
        ).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    return dict(row)


def create_auth_response(connection, user_row) -> AuthResponse:
    token, token_hash_value, expires_at = create_session_token()
    connection.execute(
        "INSERT INTO sessions (token_hash, user_id, expires_at) VALUES (?, ?, ?)",
        (token_hash_value, user_row["id"], expires_at),
    )
    return AuthResponse(access_token=token, user={"id": user_row["id"], "name": user_row["name"], "email": user_row["email"]})


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "faceframe-api"}


@app.post("/auth/register", response_model=AuthResponse, status_code=201)
def register(payload: RegisterRequest):
    with db() as connection:
        exists = connection.execute("SELECT 1 FROM users WHERE email = ?", (payload.email,)).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="An account with this email already exists")
        cursor = connection.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (payload.name.strip(), payload.email.lower(), hash_password(payload.password)),
        )
        user = connection.execute("SELECT id, name, email FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return create_auth_response(connection, user)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    with db() as connection:
        user = connection.execute("SELECT * FROM users WHERE email = ?", (payload.email.lower(),)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return create_auth_response(connection, user)


@app.post("/auth/logout", status_code=204)
def logout(authorization: Optional[str] = Header(default=None)):
    if authorization and authorization.lower().startswith("bearer "):
        with db() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(authorization.split(" ", 1)[1].strip()),))
    return Response(status_code=204)


@app.get("/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {"user": user}


@app.get("/frames")
def list_frames(shape: Optional[str] = None) -> dict:
    query = "SELECT * FROM frames"
    params: list = []
    if shape:
        query += " WHERE lower(shape) = lower(?)"
        params.append(shape)
    query += " ORDER BY match_score DESC, name"
    with db() as connection:
        rows = connection.execute(query, params).fetchall()
    return {"frames": [public_frame(row) for row in rows]}


@app.get("/saved")
def get_saved(user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        rows = connection.execute(
            "SELECT frames.* FROM saved_frames JOIN frames ON frames.id = saved_frames.frame_id WHERE user_id = ? ORDER BY saved_frames.created_at DESC",
            (user["id"],),
        ).fetchall()
    return {"frames": [public_frame(row) for row in rows]}


@app.post("/saved/{frame_id}", status_code=201)
def save_frame(frame_id: str, user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        if not connection.execute("SELECT 1 FROM frames WHERE id = ?", (frame_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Frame not found")
        connection.execute("INSERT OR IGNORE INTO saved_frames (user_id, frame_id) VALUES (?, ?)", (user["id"], frame_id))
    return {"saved": True, "frame_id": frame_id}


@app.delete("/saved/{frame_id}", status_code=204)
def unsave_frame(frame_id: str, user: dict = Depends(current_user)):
    with db() as connection:
        connection.execute("DELETE FROM saved_frames WHERE user_id = ? AND frame_id = ?", (user["id"], frame_id))
    return Response(status_code=204)


def cart_payload(connection, user_id: int) -> dict:
    rows = connection.execute(
        """SELECT frames.*, cart_items.quantity FROM cart_items
           JOIN frames ON frames.id = cart_items.frame_id
           WHERE cart_items.user_id = ? ORDER BY cart_items.updated_at DESC""",
        (user_id,),
    ).fetchall()
    items = [{"frame": public_frame(row), "quantity": row["quantity"], "line_total_cents": row["price_cents"] * row["quantity"]} for row in rows]
    return {"items": items, "item_count": sum(item["quantity"] for item in items), "total_cents": sum(item["line_total_cents"] for item in items)}


@app.get("/cart")
def get_cart(user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        return cart_payload(connection, user["id"])


@app.post("/cart/items", status_code=201)
def add_cart_item(payload: CartItemRequest, user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        frame = connection.execute("SELECT inventory_count FROM frames WHERE id = ?", (payload.frame_id,)).fetchone()
        if not frame:
            raise HTTPException(status_code=404, detail="Frame not found")
        if frame["inventory_count"] < payload.quantity:
            raise HTTPException(status_code=409, detail="Requested quantity is unavailable")
        connection.execute(
            """INSERT INTO cart_items (user_id, frame_id, quantity) VALUES (?, ?, ?)
               ON CONFLICT(user_id, frame_id) DO UPDATE SET quantity = min(quantity + excluded.quantity, 10), updated_at = CURRENT_TIMESTAMP""",
            (user["id"], payload.frame_id, payload.quantity),
        )
        return cart_payload(connection, user["id"])


@app.patch("/cart/items/{frame_id}")
def update_cart_item(frame_id: str, payload: CartQuantityRequest, user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        cursor = connection.execute("UPDATE cart_items SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND frame_id = ?", (payload.quantity, user["id"], frame_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return cart_payload(connection, user["id"])


@app.delete("/cart/items/{frame_id}", status_code=204)
def remove_cart_item(frame_id: str, user: dict = Depends(current_user)):
    with db() as connection:
        connection.execute("DELETE FROM cart_items WHERE user_id = ? AND frame_id = ?", (user["id"], frame_id))
    return Response(status_code=204)


@app.post("/orders", status_code=201)
def create_order(user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        cart = cart_payload(connection, user["id"])
        if not cart["items"]:
            raise HTTPException(status_code=409, detail="Cart is empty")
        order_id = f"ff_{uuid4().hex[:12]}"
        connection.execute("INSERT INTO orders (id, user_id, total_cents) VALUES (?, ?, ?)", (order_id, user["id"], cart["total_cents"]))
        for item in cart["items"]:
            frame = item["frame"]
            connection.execute(
                "INSERT INTO order_items (order_id, frame_id, frame_name, unit_price_cents, quantity) VALUES (?, ?, ?, ?, ?)",
                (order_id, frame["id"], frame["name"], frame["price_cents"], item["quantity"]),
            )
        connection.execute("DELETE FROM cart_items WHERE user_id = ?", (user["id"],))
        return {"order": {"id": order_id, "status": "placed", "total_cents": cart["total_cents"], "items": cart["items"]}}


@app.get("/orders")
def get_orders(user: dict = Depends(current_user)) -> dict:
    with db() as connection:
        orders = connection.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)).fetchall()
        result = []
        for order in orders:
            items = connection.execute("SELECT frame_id, frame_name, unit_price_cents, quantity FROM order_items WHERE order_id = ?", (order["id"],)).fetchall()
            result.append({**dict(order), "items": [dict(item) for item in items]})
    return {"orders": result}
