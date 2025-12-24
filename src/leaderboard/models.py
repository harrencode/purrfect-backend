from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class LeaderboardBase(BaseModel):
    user_id: UUID
    score: int
    last_active: str
    rescues: int
    adoptions: int
    lost_pets: int
    map_contributions: int
    avatar: Optional[str] = None

class LeaderboardCreate(LeaderboardBase):
    pass

class LeaderboardResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str
    score: int
    last_active: str
    rescues: int
    adoptions: int
    lost_pets: int
    map_contributions: int
    avatar: Optional[str] = None
    rank: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
