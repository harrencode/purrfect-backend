import os
import importlib
import pkgutil

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import register_routes
from .database.core import Base, engine
from .logging import LogLevels, configure_logging

configure_logging(LogLevels.info)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://192.168.1.100:3000", "http://localhost:8081"],  # front end origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from fastapi.staticfiles import StaticFiles
# app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def _startup_db_init() -> None:
    auto_create = os.getenv("AUTO_CREATE_TABLES", "false").strip().lower() in {"1", "true", "yes", "on"}
    if not auto_create:
        return

    # Ensure all models are registered on Base.metadata before create_all.
    import src.entities as entities_pkg

    for module_info in pkgutil.iter_modules(entities_pkg.__path__, entities_pkg.__name__ + "."):
        importlib.import_module(module_info.name)

    Base.metadata.create_all(bind=engine)

register_routes(app)