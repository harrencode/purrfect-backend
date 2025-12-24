from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from ..database.core import DbSession
from . import models
from . import service

router = APIRouter(
    prefix="/leaderboard",
    tags=["Leaderboard"]
)




@router.post("/", response_model=models.LeaderboardResponse, status_code=status.HTTP_201_CREATED)
def create_leaderboard_entry(db: DbSession, entry: models.LeaderboardCreate):
    return service.create_user_entry(db, entry)


@router.get("/", response_model=List[models.LeaderboardResponse])
def get_leaderboard(db: DbSession):
    return service.get_all_users(db)


@router.get("/{user_id}", response_model=models.LeaderboardResponse)
def get_leaderboard_user(db: DbSession, user_id: UUID):
    return service.get_user_entry(db, user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leaderboard_user(db: DbSession, user_id: UUID):
    service.delete_user_entry(db, user_id)
