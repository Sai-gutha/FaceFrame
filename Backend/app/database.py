import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .config import settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS sessions (
    token_hash TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS frames (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    collection_name TEXT NOT NULL,
    shape TEXT NOT NULL,
    color TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK(price_cents >= 0),
    match_score INTEGER NOT NULL CHECK(match_score BETWEEN 0 AND 100),
    image_url TEXT NOT NULL,
    inventory_count INTEGER NOT NULL DEFAULT 0 CHECK(inventory_count >= 0)
);
CREATE TABLE IF NOT EXISTS saved_frames (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frame_id TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, frame_id)
);
CREATE TABLE IF NOT EXISTS cart_items (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    frame_id TEXT NOT NULL REFERENCES frames(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, frame_id)
);
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'placed',
    total_cents INTEGER NOT NULL CHECK(total_cents >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    frame_id TEXT NOT NULL REFERENCES frames(id),
    frame_name TEXT NOT NULL,
    unit_price_cents INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    PRIMARY KEY (order_id, frame_id)
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_expires ON sessions(user_id, expires_at);
CREATE INDEX IF NOT EXISTS idx_saved_frames_user_created ON saved_frames(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_cart_items_user_updated ON cart_items(user_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_orders_user_created ON orders(user_id, created_at DESC);
"""

FRAME_SEED = [
    ("harper", "The Harper", "Everyday Edit", "Oval", "Crystal", 14900, 96, "/frames/harper-crystal.png", 24),
    ("camden", "The Camden", "Heritage", "Round", "Tortoise", 16900, 94, "/frames/camden-tortoise.png", 18),
    ("monroe", "The Monroe", "Modern Line", "Cat-eye", "Azure", 15900, 91, "/frames/monroe-azure.png", 15),
    ("ellis", "The Ellis", "Studio", "Square", "Ink", 17900, 89, "/frames/ellis-ink.png", 21),
    ("august", "The August", "Light Series", "Round", "Honey", 15500, 87, "/frames/august-honey.png", 19),
    ("rowan", "The Rowan", "Essential", "Panto", "Sage", 16500, 85, "/frames/rowan-sage.png", 17),
]


def connect() -> sqlite3.Connection:
    database_path = Path(settings.database_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 5000")
    return connection


@contextmanager
def db():
    connection = connect()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    with db() as connection:
        connection.executescript(SCHEMA)
        connection.executemany(
            """INSERT INTO frames
               (id, name, collection_name, shape, color, price_cents, match_score, image_url, inventory_count)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET
                 name=excluded.name, collection_name=excluded.collection_name,
                 shape=excluded.shape, color=excluded.color, price_cents=excluded.price_cents,
                 match_score=excluded.match_score, image_url=excluded.image_url,
                 inventory_count=excluded.inventory_count""",
            FRAME_SEED,
        )
        connection.execute("PRAGMA optimize")
