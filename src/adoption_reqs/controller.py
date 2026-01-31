from fastapi import APIRouter, UploadFile, File, Depends, status, HTTPException
from typing import List
from uuid import UUID
from ..database.core import DbSession
from . import models, service
from ..auth.service import CurrentUser
from .service import get_adoption_request_by_chat
from src.entities.pet import Pet
from src.utils.s3_service import upload_image_to_s3
from datetime import datetime, timezone
import logging

router = APIRouter(
    prefix="/adoption_reqs",
    tags=["Adoption Requests"]
)

@router.get("/all", response_model=List[models.AdoptionRequestResponse])
def get_all_adoption_requests(db: DbSession, current_user: CurrentUser):
    
    #Get all adoption requests (public).
    # If a user is logged in, exclude their own requests.
    
    user_id = current_user.get_uuid() 
    exclude_user_id=user_id
    return service.get_all_adoption_requests(db, exclude_user_id)


@router.get("/mine", response_model=List[models.AdoptionRequestResponse])
def get_my_adoption_requests(db: DbSession, current_user: CurrentUser):
    
    #Get all adoption requests created by the logged-in user.
    
    return service.get_adoption_requests(current_user, db)



@router.post("/", response_model=models.AdoptionRequestResponse, status_code=status.HTTP_201_CREATED)
def create_adoption_request(db: DbSession, adoption_req: models.AdoptionRequestCreate, current_user: CurrentUser):
    return service.create_adoption_request(current_user, db, adoption_req)

@router.get("/", response_model=List[models.AdoptionRequestResponse])
def get_adoption_requests(db: DbSession, current_user: CurrentUser):
    return service.get_adoption_requests(current_user, db)

@router.get("/{adopt_id}", response_model=models.AdoptionRequestResponse)
def get_adoption_request(db: DbSession, adopt_id: UUID, current_user: CurrentUser):
    return service.get_adoption_request_by_id(current_user, db, adopt_id)

# @router.put("/{adopt_id}", response_model=models.AdoptionRequestResponse)
# def update_adoption_request(db: DbSession, adopt_id: UUID, adoption_req_update: models.AdoptionRequestUpdate, current_user: CurrentUser, owner_id: UUID = None):
#     return service.update_adoption_request(current_user, db, adopt_id, adoption_req_update, owner_id)

@router.put("/{adopt_id}", response_model=models.AdoptionRequestResponse)
def update_adoption_request(
    db: DbSession,
    adopt_id: UUID,
    adoption_req_update: models.AdoptionRequestUpdate,
    current_user: CurrentUser,
    owner_id: UUID = None
):
    return service.update_adoption_request(current_user, db, adopt_id, adoption_req_update, owner_id)


@router.delete("/{adopt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adoption_request(db: DbSession, adopt_id: UUID, current_user: CurrentUser):
    service.delete_adoption_request(current_user, db, adopt_id)

@router.get("/by-chat/{chat_id}", response_model=models.AdoptionRequestResponse)
def get_adoption_request_by_chat(chat_id: UUID, db: DbSession, current_user: CurrentUser):
    
    # Get an adoption request linked to a chat.
    
    return service.get_adoption_request_by_chat(current_user, db, chat_id)


@router.post("/{pet_id}/upload-image")
async def upload_pet_image(
    pet_id: UUID,
    file: UploadFile ,
    db: DbSession ,
    current_user: CurrentUser,
):
    
    #Upload a pet image to S3 and attach its URL to Pet.images.
    # Expects multipart/form-data with 'file'.
    
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # only owner of pet can upload its image
    if pet.user_id != current_user.get_uuid():
        raise HTTPException(status_code=403, detail="Not allowed to modify this pet")

    try:
        # will go under pets
        url = upload_image_to_s3(file, folder="pets")
    except Exception as e:
        logging.error(f"Pet image upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to storage",
        )

    images = pet.images or []
    images.append(url)
    pet.images = images
    pet.updated_at = datetime.now(timezone.utc)

    db.add(pet)
    db.commit()
    db.refresh(pet)

    return {"url": url, "images": images}