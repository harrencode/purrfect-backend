from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from typing import List
from uuid import UUID
from src.utils.s3_service import upload_image_to_s3
from ..database.core import DbSession
from . import models, service
from ..auth.service import CurrentUser
import logging

router = APIRouter(
    prefix="/lost-found",
    tags=["Lost & Found"]
)


@router.get("/nearby", response_model=List[models.LostFoundResponse])
def get_nearby_lost_pets(
    db: DbSession,
    current_user: CurrentUser,
    lat: float,
    lon: float,
    radius_km: float = 10.0
):

    #Get nearby lost/found pets within a radius (km).
    
    return service.get_nearby_lost_pets(current_user, db, lat, lon, radius_km)


@router.post("/", response_model=models.LostFoundResponse, status_code=status.HTTP_201_CREATED)
def create_report(db: DbSession, payload: models.LostFoundCreate, current_user: CurrentUser):
    return service.create_lost_pet_report(current_user, db, payload)


@router.get("/", response_model=List[models.LostFoundResponse])
def list_reports(db: DbSession, current_user: CurrentUser):
    return service.get_lost_pets(current_user, db)


@router.get("/{report_id}", response_model=models.LostFoundResponse)
def get_report(db: DbSession, report_id: UUID, current_user: CurrentUser):
    return service.get_lost_pet_by_id(current_user, db, report_id)


@router.put("/{report_id}", response_model=models.LostFoundResponse)
def update_report(db: DbSession, report_id: UUID, payload: models.LostFoundUpdate, current_user: CurrentUser):
    return service.update_lost_pet(current_user, db, report_id, payload)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(db: DbSession, report_id: UUID, current_user: CurrentUser):
    service.delete_lost_pet(current_user, db, report_id)


@router.get("/by-chat/{chat_id}", response_model=models.LostFoundResponse)
def get_by_chat(chat_id: UUID, db: DbSession, current_user: CurrentUser):
    
    # Get a lost/found pet report linked to a specific chat.
    
    return service.get_lost_pet_by_chat(current_user, db, chat_id)

@router.post("/upload-s3")
async def upload_s3_image(
    file: UploadFile ,
    folder: str ,     # default folder for existing callers
    current_user: CurrentUser ,
):
    
    #Generic S3 image upload.
    #Used by Rescue, LostFound, Adoption etc.
    
    try:
        url = upload_image_to_s3(file, folder=folder)
        return {"url": url}
    except Exception as e:
        logging.error(f"S3 upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )