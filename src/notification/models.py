# notifications/models.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class NotificationBase(BaseModel):
    message: str

class NotificationCreate(NotificationBase):
    
    pass

class NotificationResponse(NotificationBase):
    notif_id: UUID
    user_id: UUID
    timestamp: datetime
    viewed: bool
    notif_type: str | None = None
    chat_id: UUID | None = None
    report_id: UUID | None = None

    model_config = ConfigDict(from_attributes=True)
