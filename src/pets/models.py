
from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from src.entities.pet import (
    PetType,
    PetGender,
    PetSizeEnum,
    PetTemperamentEnum,
    PetActivityLevelEnum,
)


# Base fields shared for create/read (no is_adopted here)

class PetBase(BaseModel):
    name: str
    species: PetType = PetType.Dog
    breed: Optional[str] = None
    age: Optional[int] = None  # in months
    gender: PetGender = PetGender.Unknown
    color: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = Field(default_factory=list)  
    size: Optional[PetSizeEnum] = None
    temperament: Optional[PetTemperamentEnum] = None
    activity_level: Optional[PetActivityLevelEnum] = None

    # Serialize enums as their values in responses
    model_config = ConfigDict(use_enum_values=True)



# Create: typically do NOT set is_adopted here (server defaults to False)

class PetCreate(PetBase):
    
    pass



# Update: all fields optional; allow toggling is_adopted via PUT /pets/{id}

class PetUpdate(BaseModel):
    #Used when updating an existing pet (partial update).
    name: Optional[str] = None
    species: Optional[PetType] = None
    breed: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[PetGender] = None
    color: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = None  # send [] to clear, omit to leave unchanged
    size: Optional[PetSizeEnum] = None
    temperament: Optional[PetTemperamentEnum] = None
    activity_level: Optional[PetActivityLevelEnum] = None
    is_adopted: Optional[bool] = None  # enable toggling via /pets PUT

    model_config = ConfigDict(use_enum_values=True)



# response -include is_adopted and server-managed fields

class PetResponse(PetBase):
    #Response schema for pet data.
    pet_id: UUID
    is_adopted: bool
    created_at: datetime
    updated_at: datetime
    # images already present in PetBase

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
