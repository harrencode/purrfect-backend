
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from enum import Enum
import uuid
from datetime import datetime, timezone
from ..database.core import Base
from sqlalchemy.orm import relationship


class LostFoundStatusEnum(str, Enum):
    Lost = "Lost"
    Found = "Found"
    Reunited = "Reunited"
    Archived = "Archived"


class PetGenderEnum(str, Enum):
    Male = "Male"
    Female = "Female"
    Unknown = "Unknown"


class LostFoundReport(Base):
    __tablename__ = "lost_found_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    user = relationship("User", backref="lost_found_reports")

    pet_name = Column(String, nullable=True)
    pet_type = Column(String, nullable=True)
    gender = Column(SqlEnum(PetGenderEnum), nullable=False, default=PetGenderEnum.Unknown)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photo = Column(String, nullable=True)
    status = Column(SqlEnum(LostFoundStatusEnum), nullable=False, default=LostFoundStatusEnum.Lost)
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<LostFoundReport(report_id='{self.report_id}', pet_name='{self.pet_name}', status='{self.status.value}')>"
