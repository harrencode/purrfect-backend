from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from ..entities.adoption_req import AdoptionStatus
from src.entities.pet import PetType, PetGender, PetSizeEnum, PetTemperamentEnum, PetActivityLevelEnum
import enum

# Nested pet details for adoption request
class PetCreate(BaseModel):
    name: str
    species: PetType
    size: Optional[PetSizeEnum] = None
    temperament: Optional[PetTemperamentEnum] = None
    activity_level: Optional[PetActivityLevelEnum] = None
    age: Optional[int] = None
    gender: Optional[PetGender] = PetGender.Unknown
    color: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = []

class PetResponse(PetCreate):
    pet_id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, pet):
        return cls(
            pet_id=str(pet.pet_id),
            owner_id=str(pet.user_id),
            name=pet.name,
            species=pet.species.value if isinstance(pet.species, enum.Enum) else pet.species,
            size=pet.size.value if pet.size else None,
            temperament=pet.temperament.value if pet.temperament else None,
            activity_level=pet.activity_level.value if pet.activity_level else None,
            age=pet.age,
            gender=pet.gender.value if isinstance(pet.gender, enum.Enum) else pet.gender,
            color=pet.color,
            description=pet.description,
            images=pet.images or [],
            created_at=pet.created_at,
            updated_at=pet.updated_at
        )

class AdoptionRequestBase(BaseModel):
    description: Optional[str] = None
    status: str = AdoptionStatus.Pending.value

class AdoptionRequestCreate(AdoptionRequestBase):
    pet: PetCreate  # include pet details

class AdoptionRequestUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    chat_id: Optional[str] = None

class AdoptionRequestResponse(AdoptionRequestBase):
    id: str  # adopt_id
    pet: PetResponse  # nested pet info
    chat_id: Optional[str] = None
    requester_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
