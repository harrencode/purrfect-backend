from fastapi import APIRouter, status, Form
from typing import List
from uuid import UUID
from ..database.core import DbSession
from ..auth.service import CurrentUser
from . import models, service
from .nearby_notifs import generate_nearby_notifications
import threading
import logging

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


@router.patch("/{notif_id}/viewed", response_model=models.NotificationResponse)
def mark_viewed(notif_id: UUID, db: DbSession, current_user: CurrentUser):
    return service.mark_notification_viewed(db, notif_id, current_user.get_uuid())



@router.post("/", response_model=models.NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(db: DbSession, notif: models.NotificationCreate, current_user: CurrentUser):
    return service.create_notification(current_user, db, notif)

@router.get("/", response_model=List[models.NotificationResponse])
def get_notifications(db: DbSession, current_user: CurrentUser):
    return service.get_notifications(current_user, db)

@router.get("/{notif_id}", response_model=models.NotificationResponse)
def get_notification(db: DbSession, notif_id: UUID, current_user: CurrentUser):
    return service.get_notification_by_id(current_user, db, notif_id)


@router.post("/nearby", status_code=status.HTTP_202_ACCEPTED)
def trigger_nearby_notifications(
    db: DbSession,
    current_user: CurrentUser,
    latitude: float = Form(...),
    longitude: float = Form(...),
):
    
    #Kick off generation of nearby notifications for the current user
    #based on their latitude/longitude. Runs in a background thread.
    

    def _run():
        try:
            # current_user here is your TokenData / CurrentUser alias
            # generate_nearby_notifications is already written to handle that
            generate_nearby_notifications(db, current_user, latitude, longitude)
        except Exception as e:
            logging.error(f"[Nearby] Failed to generate nearby notifications: {e}")

    threading.Thread(target=_run, daemon=True).start()

    return {"detail": "Nearby notification generation started"}