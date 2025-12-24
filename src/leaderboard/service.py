from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from . import models
from src.entities.leaderboard import LeaderboardUser
from src.entities.user import User
import logging


def create_user_entry(db: Session, data: models.LeaderboardCreate) -> LeaderboardUser:
    # Ensure user exists
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        new_entry = LeaderboardUser(**data.model_dump())
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        logging.info(f"Created leaderboard entry for user {user.first_name} {user.last_name}")
        return new_entry
    except Exception as e:
        logging.error(f"Error creating leaderboard entry: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def get_all_users(db: Session) -> list[models.LeaderboardResponse]:
    entries = db.query(LeaderboardUser).join(User).order_by(LeaderboardUser.score.desc()).all()
    
    # Compute rank dynamically
    response = []
    for index, entry in enumerate(entries, start=1):
        response.append(models.LeaderboardResponse(
            id=entry.id,
            user_id=entry.user_id,
            full_name=f"{entry.user.first_name} {entry.user.last_name}",
            score=entry.score,
            last_active=entry.last_active,
            rescues=entry.rescues,
            adoptions=entry.adoptions,
            lost_pets=entry.lost_pets,
            map_contributions=entry.map_contributions,
            avatar=entry.avatar,
            rank=index
        ))
    return response


def get_user_entry(db: Session, user_id: UUID) -> models.LeaderboardResponse:
    entry = db.query(LeaderboardUser).join(User).filter(LeaderboardUser.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")

    # Compute rank
    rank = db.query(LeaderboardUser).filter(LeaderboardUser.score > entry.score).count() + 1

    return models.LeaderboardResponse(
        id=entry.id,
        user_id=entry.user_id,
        full_name=f"{entry.user.first_name} {entry.user.last_name}",
        score=entry.score,
        last_active=entry.last_active,
        rescues=entry.rescues,
        adoptions=entry.adoptions,
        lost_pets=entry.lost_pets,
        map_contributions=entry.map_contributions,
        avatar=entry.avatar,
        rank=rank
    )


def delete_user_entry(db: Session, user_id: UUID):
    entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == user_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Leaderboard entry not found")
    db.delete(entry)
    db.commit()
    logging.info(f"Deleted leaderboard entry for user {user_id}")
