from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SqlEnum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from enum import Enum
import uuid
from datetime import datetime, timezone
from ..database.core import Base

class ChatTypeEnum(str, Enum):
    Rescue = "rescue"
    Adoption = "adoption"
    LostPet = "lostpet"
    Generic = "generic"

class Chat(Base):
    __tablename__ = "chats"
    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_type = Column(SqlEnum(ChatTypeEnum), nullable=False, default=ChatTypeEnum.Generic)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    members = relationship("ChatMember", back_populates="chat", cascade="all,delete-orphan")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all,delete-orphan")

class ChatMember(Base):
    __tablename__ = "chat_members"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="members")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="messages")
