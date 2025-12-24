from fastapi import FastAPI
from .database.core import engine, Base
from .entities.user import User  
from .api import register_routes
from .logging import configure_logging, LogLevels
from fastapi.middleware.cors import CORSMiddleware  

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



# Only uncomment below to create new tables, 
#otherwise the tests will fail if not connected

Base.metadata.create_all(bind=engine)

register_routes(app)