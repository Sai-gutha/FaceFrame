import importlib

from fastapi.testclient import TestClient


def make_client(tmp_path, monkeypatch):
    monkeypatch.setenv("FACEFRAME_DATABASE_PATH", str(tmp_path / "test.db"))
    import app.config
    import app.database
    import app.main
    importlib.reload(app.config)
    importlib.reload(app.database)
    importlib.reload(app.main)
    return TestClient(app.main.app)


def auth_headers(client):
    response = client.post("/auth/register", json={"name": "Alex Morgan", "email": "alex@example.com", "password": "secure-pass-123"})
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_health_and_frame_catalog(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch) as client:
        assert client.get("/health").json()["status"] == "ok"
        frames = client.get("/frames").json()["frames"]
        assert len(frames) == 6
        assert frames[0]["id"] == "harper"


def test_registration_login_and_protected_profile(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch) as client:
        headers = auth_headers(client)
        assert client.get("/me", headers=headers).json()["user"]["email"] == "alex@example.com"
        duplicate = client.post("/auth/register", json={"name": "Alex Morgan", "email": "alex@example.com", "password": "secure-pass-123"})
        assert duplicate.status_code == 409
        login = client.post("/auth/login", json={"email": "alex@example.com", "password": "secure-pass-123"})
        assert login.status_code == 200


def test_saved_cart_and_order_flow(tmp_path, monkeypatch):
    with make_client(tmp_path, monkeypatch) as client:
        headers = auth_headers(client)
        assert client.post("/saved/camden", headers=headers).status_code == 201
        assert client.get("/saved", headers=headers).json()["frames"][0]["id"] == "camden"
        cart = client.post("/cart/items", headers=headers, json={"frame_id": "harper", "quantity": 2})
        assert cart.status_code == 201
        assert cart.json()["total_cents"] == 29800
        order = client.post("/orders", headers=headers)
        assert order.status_code == 201
        assert order.json()["order"]["total_cents"] == 29800
        assert client.get("/cart", headers=headers).json()["item_count"] == 0
        assert len(client.get("/orders", headers=headers).json()["orders"]) == 1
