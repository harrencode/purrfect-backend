from fastapi import APIRouter, status
from typing import List
from uuid import UUID

from ..database.core import DbSession
from . import models
from . import service
from ..auth.service import CurrentUser
from src.utils.s3_service import upload_image_to_s3
from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import UploadFile, File

router = APIRouter(
    prefix="/pets",
    tags=["Pets"]
)

@router.post("/", response_model=models.PetResponse, status_code=status.HTTP_201_CREATED)
def create_pet(db: DbSession, pet: models.PetCreate, current_user: CurrentUser):
    #Create a new pet for the current user.
    return service.create_pet(current_user, db, pet)


@router.get("/", response_model=List[models.PetResponse])
def get_pets(db: DbSession, current_user: CurrentUser):
    #Get all pets owned by the current user.
    return service.get_pets(current_user, db)


@router.get("/{pet_id}", response_model=models.PetResponse)
def get_pet(db: DbSession, pet_id: UUID, current_user: CurrentUser):
    #Get a single pet by ID.
    return service.get_pet_by_id(current_user, db, pet_id)


@router.put("/{pet_id}", response_model=models.PetResponse)
def update_pet(db: DbSession, pet_id: UUID, pet_update: models.PetUpdate, current_user: CurrentUser):
    #Update pet details.
    return service.update_pet(current_user, db, pet_id, pet_update)


@router.put("/{pet_id}/adopt", response_model=models.PetResponse)
def adopt_pet(db: DbSession, pet_id: UUID, current_user: CurrentUser):
    #Mark a pet as adopted.
    return service.adopt_pet(current_user, db, pet_id)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(db: DbSession, pet_id: UUID, current_user: CurrentUser):
    #Delete a pet.
    service.delete_pet(current_user, db, pet_id)


@router.post("/{pet_id}/upload-image")
def upload_pet_image(pet_id: UUID, db: DbSession, current_user: CurrentUser, file: UploadFile = File(...)):
    #Upload image to AWS S3 and attach to pet
    pet = service.get_pet_by_id(current_user, db, pet_id)

    file_url = upload_image_to_s3(file, folder="pet_images")

    pet.images = pet.images + [file_url] if pet.images else [file_url]
    db.commit()
    db.refresh(pet)

    return {"message": "Image uploaded", "image_url": file_url}