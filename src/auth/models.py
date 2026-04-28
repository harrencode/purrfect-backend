from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from ..entities.user import PreferredSpeciesEnum, PreferredSizeEnum, TemperamentEnum, ActivityLevelEnum

class RegisterUserRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


     # New optional fields
    preferred_species: Optional[PreferredSpeciesEnum] = PreferredSpeciesEnum.Any
    preferred_size: Optional[PreferredSizeEnum] = PreferredSizeEnum.Any
    temperament: Optional[TemperamentEnum] = PreferredSpeciesEnum.Any
    activity_level: Optional[ActivityLevelEnum] = PreferredSpeciesEnum.Any
    min_age: Optional[int] = None
    max_age: Optional[int] = None

    # Image upload (as base64 or multipart)
    profile_image: Optional[str] = None  # Can also use UploadFile if use multipart/form-data

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id: str | None = None

    def get_uuid(self) -> UUID | None:
        if self.user_id:
            return UUID(self.user_id)
        return None
    

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class ResendCodeRequest(BaseModel):
    email: EmailStr