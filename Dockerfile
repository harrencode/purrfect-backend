# Build stage
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY src/ src/

COPY alembic.ini .
COPY alembic/ alembic/

# Expose the port FastAPI runs on
EXPOSE 8000

# Run migrations, optionally seed an admin user, train fallback recommender artifacts, then start the API.
# Uses PORT if provided by the hosting platform.
CMD ["sh", "-c", "alembic upgrade head && python -m src.scripts.create_admin && python -m src.recommender.scripts.train && gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} src.main:app"]
