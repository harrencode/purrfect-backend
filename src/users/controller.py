
from fastapi import APIRouter, status, HTTPException
from uuid import UUID
from ..database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=models.UserResponse)
def get_current_user(current_user: CurrentUser, db: DbSession):
    user_uuid = current_user.get_uuid()
    if user_uuid is None:
        # token is missing/invalid
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing user in token",
        )

    return service.get_user_by_id(db, user_uuid)

@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_change: models.PasswordChange,
    db: DbSession,
    current_user: CurrentUser
):
    service.change_password(db, current_user.get_uuid(), password_change)

# Update user preferences
@router.put("/preferences", response_model=models.UserResponse)
def update_preferences(
    preferences: models.UserPreferenceUpdate,
    db: DbSession,
    current_user: CurrentUser
):
    return service.update_preferences(db, current_user.get_uuid(), preferences)

@router.get("/", response_model=list[models.UserResponse])
def get_all_users(
    db: DbSession,
    current_user: CurrentUser
):
    return service.get_all_users(db)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def soft_delete_user(
    user_id: UUID,
    db: DbSession,
    current_user: CurrentUser
):
    #  ensure only admins can delete
    me = service.get_user_by_id(db, current_user.get_uuid())
    if not me.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # prevent self-deletion 
    if me.id == user_id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself")

    service.soft_delete_user(db, user_id)