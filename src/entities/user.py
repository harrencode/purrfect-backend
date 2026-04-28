
import uuid
import enum
from sqlalchemy import Column, String, Integer, Enum, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from ..database.core import Base


class PreferredSpeciesEnum(enum.Enum):
    Dog = "dog"
    Cat = "cat"
    Any = "any"

class PreferredSizeEnum(enum.Enum):
    Small = "small"
    Medium = "medium"
    Large = "large"
    Any = "any"

class ActivityLevelEnum(enum.Enum):
    Low = "low"
    Moderate = "moderate"
    High = "high"
    Any = "any"

class TemperamentEnum(enum.Enum):
    Calm = "calm"
    Playful = "playful"
    Friendly = "friendly"
    Energetic = "energetic"
    Gentle = "gentle"
    Any = "any"

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    profile_photo_url = Column(String, nullable=True, default="https://avatar.iran.liara.run/public/11")

    # Preference fields
    preferred_species = Column(Enum(PreferredSpeciesEnum), default=PreferredSpeciesEnum.Any, nullable=True)
    preferred_size = Column(Enum(PreferredSizeEnum), default=PreferredSizeEnum.Any, nullable=True)
    temperament = Column(Enum(TemperamentEnum), default=TemperamentEnum.Any, nullable=True)
    activity_level = Column(Enum(ActivityLevelEnum), default=ActivityLevelEnum.Any, nullable=True)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    is_admin = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # fcm_token = Column(String, nullable=True)


    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String, nullable=True, unique=True)
    email_verification_expires_at = Column(DateTime(timezone=True), nullable=True)
    email_verification_attempts = Column(Integer, default=0, nullable=False)

    def __repr__(self):
        return f"<User(email='{self.email}', first_name='{self.first_name}', last_name='{self.last_name}')>"
