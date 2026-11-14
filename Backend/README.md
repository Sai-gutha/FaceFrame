# FaceFrame Backend

FastAPI backend for the FaceFrame customer experience. It provides account sessions, frame inventory, saved frames, cart state, and orders using SQLite.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000/docs` for the interactive API reference.

## API groups

- `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`
- `GET /me`
- `GET /frames`
- `GET|POST|DELETE /saved`
- `GET|POST|PATCH|DELETE /cart`
- `GET|POST /orders`

Copy `.env.example` to `.env` and adjust the database path, allowed origins, and session lifetime for deployment.
