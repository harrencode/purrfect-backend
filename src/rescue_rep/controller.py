from fastapi import APIRouter, status, UploadFile, File, Depends, HTTPException
from typing import List
from uuid import UUID

from ..database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser
from src.utils.s3_service import upload_image_to_s3

router = APIRouter(
    prefix="/rescue-rep",
    tags=["Rescue Reports"]
)


@router.get("/nearby", response_model=List[models.RescueReportResponse])
def get_nearby_rescue_reports(
    db: DbSession,
    current_user: CurrentUser,
    lat: float,
    lon: float,
    radius_km: float = 10.0,  # default 10 km radius
):
    
    # Get rescue reports near the given latitude/longitude.
    
    return service.get_nearby_rescue_reports(current_user, db, lat, lon, radius_km)


@router.post("/", response_model=models.RescueReportResponse, status_code=status.HTTP_201_CREATED)
def create_rescue_report(db: DbSession, rescue_report: models.RescueReportCreate, current_user: CurrentUser):
    
    #Create a new rescue report.
    
    return service.create_rescue_report(current_user, db, rescue_report)


@router.get("/", response_model=List[models.RescueReportResponse])
def get_rescue_reports(db: DbSession, current_user: CurrentUser):
    
    #Get all rescue reports created by the current user.
    
    return service.get_rescue_reports(current_user, db)


@router.get("/{report_id}", response_model=models.RescueReportResponse)
def get_rescue_report(db: DbSession, report_id: UUID, current_user: CurrentUser):
    
    #Get a specific rescue report by ID.
    
    return service.get_rescue_report_by_id(current_user, db, report_id)


@router.put("/{report_id}", response_model=models.RescueReportResponse)
def update_rescue_report(db: DbSession, report_id: UUID, rescue_report_update: models.RescueReportUpdate, current_user: CurrentUser):
    
    #Update an existing rescue report.
    
    return service.update_rescue_report(current_user, db, report_id, rescue_report_update)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rescue_report(db: DbSession, report_id: UUID, current_user: CurrentUser):
    
    #Delete a rescue report by ID.
    
    service.delete_rescue_report(current_user, db, report_id)



@router.get("/by-chat/{chat_id}", response_model=models.RescueReportResponse)
def get_rescue_report_by_chat(chat_id: UUID, db: DbSession, current_user: CurrentUser):
    
    #Get a rescue report linked to a chat.
    
    return service.get_rescue_report_by_chat(current_user, db, chat_id)

@router.post("/upload-s3")
async def upload_rescue_image(
    file: UploadFile,
    current_user: CurrentUser  
):
    
    #Upload a rescue photo to S3 and return its public URL.
    #Expects multipart/form-data with a 'file' field.
    
    try:
        # Store rescue photos under 'rescues/' folder in your bucket
        url = upload_image_to_s3(file, folder="rescues")
        return {"url": url}
    except Exception as e:
        import logging
        logging.error(f"Rescue image upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image",
        )