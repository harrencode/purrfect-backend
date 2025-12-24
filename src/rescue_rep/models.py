
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class RescueReportBase(BaseModel):
    location: str
    latitude: Optional[float] = None  
    longitude: Optional[float] = None  
    photo: Optional[str] = None
    status: str
    description: Optional[str] = None
    alert_type: str

class RescueReportCreate(RescueReportBase):
    pass

class RescueReportUpdate(BaseModel):
    location: Optional[str] = None
    photo: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    alert_type: Optional[str] = None

class RescueReportResponse(RescueReportBase):
    reportId: UUID
    userId: UUID
    chatId: Optional[UUID] = None  
    userFirstName: Optional[str] = None  
    userLastName: Optional[str] = None
    userFullName: Optional[str] = None  # Optional combined full name


    class Config:
        orm_mode = True
