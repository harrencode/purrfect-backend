# Purrfect Backend

FastAPI backend powering the Purrfect app (auth, users, pets, adoption requests, rescue reps, notifications, store/cart, chat, leaderboard, lost & found, stray map, stats, and recommendations).

## Tech

- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + PostgreSQL (Docker Compose)
- Pytest (unit + e2e tests)

## Deploy to AWS (ECS + RDS) with GitHub Actions

This repo is ready to run as a Docker container on **Amazon ECS** (typically Fargate) and use **Amazon RDS PostgreSQL**.

### 1) Create an RDS PostgreSQL database

- Create an RDS PostgreSQL instance in the same VPC as your ECS tasks.
- Ensure the RDS Security Group allows inbound PostgreSQL (5432) from the ECS tasks' Security Group.

### 2) Create ECR + ECS resources

You’ll need (in AWS):

- An **ECR repository** (to store the Docker image)
- An **ECS cluster** and **ECS service**
- (Recommended) An **Application Load Balancer** targeting the ECS service

The container listens on port `8000` and exposes a health endpoint at `/health`.

### 3) Configure your ECS task definition

Use the template in [ecs/task-definition.json](ecs/task-definition.json) and replace the `REPLACE_ME_...` fields:

- `executionRoleArn`: ECS task execution role (pull from ECR, write logs)
- `taskRoleArn`: app role (S3 access etc.)
- `secrets`: point to AWS Secrets Manager / SSM parameters for `DATABASE_URL` and `SECRET_KEY`
- `awslogs-region`: set your region

### 4) Configure GitHub Actions (recommended via OIDC)

The workflow [deploy-ecs.yml](.github/workflows/deploy-ecs.yml) builds/pushes to ECR and updates the ECS service.

In your GitHub repo, set these **Secrets**:

- `AWS_REGION`
- `AWS_ROLE_TO_ASSUME` (IAM role that GitHub OIDC can assume)
- `ECR_REPOSITORY`
- `ECS_CLUSTER`
- `ECS_SERVICE`

After that, pushing to `main` will deploy.

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

The SQLAlchemy connection string is read from `DATABASE_URL` (recommended for production and required for RDS). If `DATABASE_URL` is not set, it defaults to the Docker Compose Postgres URL.

If you run via Docker Compose, Postgres is available at:

`postgresql://postgres:postgres@db:5432/cleanfastapi`

### Migrations (Alembic)

- Alembic is configured via [alembic.ini](alembic.ini) and [alembic/env.py](alembic/env.py).
- For ECS, run migrations as a one-off task (recommended) or exec into a running task and run `alembic upgrade head`.

### Schema creation

For local development with Docker Compose, `AUTO_CREATE_TABLES=true` is set in [docker-compose.yml](docker-compose.yml) so tables are created on startup.

For production (RDS), keep `AUTO_CREATE_TABLES=false` and manage schema using migrations (Alembic) or a one-time admin job.

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