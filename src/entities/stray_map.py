from sqlalchemy import Column, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import uuid
import enum

from ..database.core import Base

class LocationType(enum.Enum):
    rescue_home = "rescue_home"
    stray_animal = "stray_animal"
    vet_center = "vet_center"



class StrayMapEntry(Base):
    __tablename__ = "stray_map_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    contact_info = Column(String, nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    location_type = Column(Enum(LocationType), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<StrayMapEntry(name='{self.name}', type='{self.location_type}', lat={self.latitude}, lng={self.longitude})>"
