# src/recommender/models.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List

class PetResponse(BaseModel):
    pet_id: UUID
    name: str
    species: str
    breed: Optional[str]
    age: Optional[int]
    gender: str
    color: Optional[str]
    size: Optional[str]
    temperament: Optional[str]
    activity_level: Optional[str]
    description: Optional[str]
    images: List[str] = [] 


