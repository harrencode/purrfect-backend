from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class LostFoundBase(BaseModel):
    pet_name: Optional[str] = None
    pet_type: Optional[str] = None
    gender: Optional[str] = "Unknown"
    description: Optional[str] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo: Optional[str] = None
    status: Optional[str] = "Lost"


class LostFoundCreate(LostFoundBase):
    pass


class LostFoundUpdate(BaseModel):
    pet_name: Optional[str] = None
    pet_type: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photo: Optional[str] = None
    status: Optional[str] = None
    chat_id: Optional[UUID] = None


class LostFoundResponse(LostFoundBase):
    reportId: UUID
    userId: UUID
    chatId: Optional[UUID] = None
    userFirstName: Optional[str] = None
    userLastName: Optional[str] = None
    userFullName: Optional[str] = None

    class Config:
        orm_mode = True
