# Purrfect Backend

FastAPI backend powering the Purrfect app (auth, users, pets, adoption requests, rescue reps, notifications, store/cart, chat, leaderboard, lost & found, stray map, stats, and recommendations).

## Tech

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL (Docker Compose)
- Pytest (unit + e2e tests)

## Quickstart (Docker)

Prereqs: Docker Desktop

1) Start API + Postgres (+ pgAdmin):

```bash
docker compose up --build
```

2) Open API docs:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Stop services:

```bash
docker compose down
```

pgAdmin (optional): http://localhost:8080

## Local setup (no Docker)

Prereqs: Python 3.11+

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

Run the API:

```bash
uvicorn src.main:app --reload
```

### Database configuration

The SQLAlchemy connection string is currently hard-coded in [src/database/core.py](src/database/core.py). If you want to configure it via environment variables (recommended), update that file to read `DATABASE_URL` from your `.env` / environment.

If you run via Docker Compose, Postgres is available at:

`postgresql://postgres:postgres@db:5432/cleanfastapi`

If you run locally without Docker, you’ll need a reachable Postgres instance or switch to SQLite in [src/database/core.py](src/database/core.py).

## Environment variables

Docker Compose passes these into the API container (see [docker-compose.yml](docker-compose.yml)):

- `DATABASE_URL`
- `WHATSAPP_NUMBER`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_S3_BUCKET_NAME`
- `AWS_REGION`

## Tests

Run all tests:

```bash
pytest
```

## Project layout

- `src/main.py`: FastAPI app + middleware registration
- `src/api.py`: router registration
- `src/*/controller.py`: route handlers by feature
- `src/*/service.py`: business logic
- `src/entities/`: SQLAlchemy models
- `tests/`: unit tests and `tests/e2e/` endpoint tests