
# src/entities/rescue_rep.py
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
import uuid
from datetime import datetime, timezone
from ..database.core import Base
from sqlalchemy.orm import relationship

class RescueStatusEnum(str, Enum):
    Pending = "Pending"
    InProgress = "InProgress"
    Resolved = "Resolved"
    Rejected = "Rejected"

class RescueAlertTypeEnum(str, Enum):
    Critical = "Critical"
    High = "High"
    Medium = "Medium"
    Low = "Low"

class RescueReport(Base):
    __tablename__ = "rescue_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="rescue_reports")  
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)  
    longitude = Column(Float, nullable=True) 
    photo = Column(String, nullable=True)
    status = Column(SqlEnum(RescueStatusEnum), nullable=False, default=RescueStatusEnum.Pending)
    alert_type = Column(SqlEnum(RescueAlertTypeEnum), nullable=False, default=RescueAlertTypeEnum.Medium)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<RescueReport(report_id='{self.report_id}', status='{self.status.value}', chat_id='{self.chat_id}')>"
