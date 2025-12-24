from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class ChatCreate(BaseModel):
    chat_type: str
    related_entity_id: Optional[UUID] = None

class ChatResponse(BaseModel):
    chatId: UUID
    chat_type: str
    related_entity_id: Optional[UUID]
    creator_id: UUID
    members: Optional[List[UUID]] = []
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    messageId: UUID
    chatId: UUID
    senderId: UUID
    content: str
    created_at: datetime

    class Config:
        orm_mode = True
