
from sqlalchemy import JSON, Column, String, Boolean, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
import enum
from ..database.core import Base



class PetType(enum.Enum):
    Dog = "Dog"
    Cat = "Cat"
    # Bird = "Bird"
    # Rabbit = "Rabbit"
    Other = "Other"


class PetGender(enum.Enum):
    Male = "Male"
    Female = "Female"
    Unknown = "Unknown"


class PetSizeEnum(enum.Enum):
    small = "small"
    medium = "medium"
    large = "large"


class PetTemperamentEnum(enum.Enum):
    calm = "calm"
    playful = "playful"
    friendly = "friendly"
    energetic = "energetic"
    gentle = "gentle"


class PetActivityLevelEnum(enum.Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class Pet(Base):
    __tablename__ = "pets"

    pet_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    species = Column(Enum(PetType), nullable=False, default=PetType.Dog)
    breed = Column(String, nullable=True)
    age = Column(Integer, nullable=True)  # in months

    gender = Column(Enum(PetGender), nullable=False, default=PetGender.Unknown)
    color = Column(String, nullable=True)

    # Added fields to match preferences
    size = Column(Enum(PetSizeEnum), nullable=True)
    temperament = Column(Enum(PetTemperamentEnum), nullable=True)
    activity_level = Column(Enum(PetActivityLevelEnum), nullable=True)

    description = Column(String, nullable=True)
    is_adopted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    # image_url = Column(String, nullable=True)
    images = Column(JSON, default=list)  # Add this

    def __repr__(self):
        return f"<Pet(name='{self.name}', species='{self.species.value}', adopted={self.is_adopted})>"
