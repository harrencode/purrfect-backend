from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.auth.models import TokenData
from src.entities.pet import Pet
from src.exceptions import PetCreationError, PetNotFoundError
import logging


def create_pet(current_user: TokenData, db: Session, pet: models.PetCreate) -> Pet:
    #Create a new pet for the current user.
    try:
        new_pet = Pet(**pet.model_dump())
        new_pet.user_id = current_user.get_uuid()
        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)
        logging.info(f"Created new pet for user: {current_user.get_uuid()}")
        return new_pet
    except Exception as e:
        logging.error(f"Failed to create pet for user {current_user.get_uuid()}. Error: {str(e)}")
        raise PetCreationError(str(e))


def get_pets(current_user: TokenData, db: Session) -> list[models.PetResponse]:
    #Retrieve all pets belonging to the current user.
    pets = db.query(Pet).filter(Pet.user_id == current_user.get_uuid()).all()
    logging.info(f"Retrieved {len(pets)} pets for user: {current_user.get_uuid()}")
    return pets


def get_pet_by_id(current_user: TokenData, db: Session, pet_id: UUID) -> Pet:
    #Retrieve a single pet by ID.
    pet = db.query(Pet).filter(Pet.pet_id == pet_id).filter(Pet.user_id == current_user.get_uuid()).first()
    if not pet:
        logging.warning(f"Pet {pet_id} not found for user {current_user.get_uuid()}")
        raise PetNotFoundError(pet_id)
    logging.info(f"Retrieved pet {pet_id} for user {current_user.get_uuid()}")
    return pet


def update_pet(current_user: TokenData, db: Session, pet_id: UUID, pet_update: models.PetUpdate) -> Pet:
    #Update an existing pet’s details.
    pet_data = pet_update.model_dump(exclude_unset=True)
    db.query(Pet).filter(Pet.pet_id == pet_id).filter(Pet.user_id == current_user.get_uuid()).update(pet_data)
    db.commit()
    logging.info(f"Successfully updated pet {pet_id} for user {current_user.get_uuid()}")
    return get_pet_by_id(current_user, db, pet_id)


def adopt_pet(current_user: TokenData, db: Session, pet_id: UUID) -> Pet:
    #Mark a pet as adopted
    pet = get_pet_by_id(current_user, db, pet_id)
    if pet.is_adopted:
        logging.debug(f"Pet {pet_id} is already adopted")
        return pet
    pet.is_adopted = True
    pet.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(pet)
    logging.info(f"Pet {pet_id} marked as adopted by user {current_user.get_uuid()}")
    return pet


def delete_pet(current_user: TokenData, db: Session, pet_id: UUID) -> None:
    #Delete a pet record.
    pet = get_pet_by_id(current_user, db, pet_id)
    db.delete(pet)
    db.commit()
    logging.info(f"Pet {pet_id} deleted by user {current_user.get_uuid()}")
    return HTTPException(status_code=204, detail="Pet deleted successfully")