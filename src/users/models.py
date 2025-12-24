# from pydantic import BaseModel, EmailStr
# from uuid import UUID
# from datetime import datetime


# class UserResponse(BaseModel):
#     id: UUID
#     email: EmailStr
#     first_name: str
#     last_name: str


# class PasswordChange(BaseModel):
#     current_password: str
#     new_password: str
#     new_password_confirm: str


from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional
from src.entities.user import PreferredSpeciesEnum, PreferredSizeEnum, TemperamentEnum, ActivityLevelEnum


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    profile_photo_url: Optional[str] = "https://avatar.iran.liara.run/public/11"
    is_admin: bool = False
    is_active: bool = True

    # Preference fields added
    preferred_species: Optional[PreferredSpeciesEnum] = PreferredSpeciesEnum.Any
    preferred_size: Optional[PreferredSizeEnum] = PreferredSizeEnum.Any
    temperament: Optional[TemperamentEnum] = TemperamentEnum.Any
    activity_level: Optional[ActivityLevelEnum] = ActivityLevelEnum.Any
    min_age: Optional[int] = None
    max_age: Optional[int] = None


class UserResponse(UserBase):
    id: UUID


class UserPreferenceUpdate(BaseModel):
    preferred_species: Optional[PreferredSpeciesEnum] = None
    preferred_size: Optional[PreferredSizeEnum] = None
    temperament: Optional[TemperamentEnum] = None
    activity_level: Optional[ActivityLevelEnum] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
