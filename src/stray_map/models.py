
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.entities.stray_map import LocationType


class StrayMapBase(BaseModel):
    name: str = Field(..., example="Happy Paws Rescue")
    description: Optional[str] = Field(None, example="Small rescue home with 10 dogs")
    contact_info: Optional[str] = Field(None, example="0771234567")
    latitude: float = Field(..., example=6.9271)
    longitude: float = Field(..., example=79.8612)
    location_type: LocationType


class StrayMapCreate(StrayMapBase):
    
    pass


class StrayMapResponse(StrayMapBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)
