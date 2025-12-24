from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from datetime import datetime, timezone

from src.auth.models import TokenData
from src.entities.stray_map import StrayMapEntry
from . import models

from src.entities.leaderboard import LeaderboardUser
import logging


def create_entry(current_user: TokenData, db: Session, entry_data: models.StrayMapCreate) -> StrayMapEntry:
    try:
        new_entry = StrayMapEntry(**entry_data.model_dump())
        new_entry.user_id = current_user.get_uuid()

        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)

        logging.info(f"Created {entry_data.location_type} entry for user {current_user.get_uuid()}")

        # Update leaderboard for the user who added the map entry
        try:
            now_str = datetime.now(timezone.utc).isoformat()
            user_id = current_user.get_uuid()
            POINTS_FOR_MAP_ENTRY = 10  #  points for adding a stray map entry

            entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == user_id).first()

            if entry:
                entry.score += POINTS_FOR_MAP_ENTRY
                entry.map_contributions = (entry.map_contributions or 0) + 1
                entry.last_active = now_str
            else:
                new_leaderboard_entry = LeaderboardUser(
                    user_id=user_id,
                    score=POINTS_FOR_MAP_ENTRY,
                    rescues=0,
                    adoptions=0,
                    lost_pets=0,
                    map_contributions=1,
                    avatar=None,
                    last_active=now_str,
                )
                db.add(new_leaderboard_entry)

            db.commit()
            logging.info(f"Leaderboard updated: +{POINTS_FOR_MAP_ENTRY} for user {user_id} (stray map entry)")

        except Exception as e:
            db.rollback()
            logging.error(f"Failed to update leaderboard after stray map entry: {e}")

        return new_entry

    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create entry: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create entry: {str(e)}")



def get_entries(db: Session, location_type: str | None = None):
    query = db.query(StrayMapEntry)
    if location_type:
        query = query.filter(StrayMapEntry.location_type == location_type)
    return query.all()


def get_entry_by_id(db: Session, entry_id: UUID):
    entry = db.query(StrayMapEntry).filter(StrayMapEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


def delete_entry(current_user: TokenData, db: Session, entry_id: UUID):
    entry = get_entry_by_id(db, entry_id)
    if entry.user_id != current_user.get_uuid():
        raise HTTPException(status_code=403, detail="Not authorized to delete this entry")
    db.delete(entry)
    db.commit()
    logging.info(f"Deleted entry {entry_id} by user {current_user.get_uuid()}")
