# src/entities/notification.py
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
from ..database.core import Base

class Notification(Base):
    __tablename__ = "notifications"

    notif_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    notif_type = Column(String, nullable=True)  # "rescue" or "lostpet"
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=True)
    report_id = Column(UUID(as_uuid=True), nullable=True)
    viewed = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

