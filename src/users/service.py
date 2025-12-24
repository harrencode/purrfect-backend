
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.entities.user import User
from src.exceptions import UserNotFoundError, InvalidPasswordError, PasswordMismatchError
from src.auth.service import verify_password, get_password_hash
import logging


def get_user_by_id(db: Session, user_id: UUID) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logging.warning(f"User not found with ID: {user_id}")
        raise UserNotFoundError(user_id)
    return user


def change_password(db: Session, user_id: UUID, password_change: models.PasswordChange) -> None:
    user = get_user_by_id(db, user_id)

    if not verify_password(password_change.current_password, user.password_hash):
        raise InvalidPasswordError()

    if password_change.new_password != password_change.new_password_confirm:
        raise PasswordMismatchError()

    user.password_hash = get_password_hash(password_change.new_password)
    db.commit()


# Update preferences
def update_preferences(db: Session, user_id: UUID, preferences: models.UserPreferenceUpdate) -> User:
    user = get_user_by_id(db, user_id)
    updates = preferences.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    logging.info(f"Updated preferences for user {user_id}")
    return user

def get_all_users(db: Session) -> list[User]:
    users = db.query(User).filter(User.is_active == True).all()
    logging.info(f"Retrieved active users, count: {len(users)}")
    return users

def soft_delete_user(db: Session, user_id: UUID) -> None:
    user = get_user_by_id(db, user_id)

    if not user.is_active:
        logging.info(f"User {user_id} already inactive")
        return

    user.is_active = False
    db.commit()
    logging.info(f"Soft-deleted user {user_id}")