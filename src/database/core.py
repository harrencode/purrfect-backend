from typing import Annotated

import os

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()


def _build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")

    if user and password and db_name:
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

    raise ValueError("DATABASE_URL or POSTGRES_* environment variables must be set")


DATABASE_URL = _build_database_url()


def _build_engine(database_url: str):
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )

    connect_args: dict[str, str] = {}

    # Useful for RDS (e.g., require or verify-full). If already in URL, psycopg2 will use it.
    sslmode = os.getenv("DB_SSLMODE")
    if sslmode and "sslmode=" not in database_url:
        connect_args["sslmode"] = sslmode

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        connect_args=connect_args,
    )


engine = _build_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
DbSession = Annotated[Session, Depends(get_db)]

