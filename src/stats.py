# FastAPI route to compute the three numbers using SQLAlchemy models.

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, select


from .entities.rescue_rep import RescueReport, RescueStatusEnum
from .entities.adoption_req import AdoptionRequest, AdoptionStatus
from .entities.stray_map import StrayMapEntry, LocationType


from .database.core import get_db  

router = APIRouter(prefix="/api", tags=["stats"])

class StatsOut(BaseModel):
    rescues: int
    adoptions: int
    located: int

@router.get("/stats", response_model=StatsOut)
def get_stats(db: Session = Depends(get_db)) -> StatsOut:
    # Rescues resolved rescue reports
    rescues_q = (
        select(func.count())
        .select_from(RescueReport)
        .where(RescueReport.status == RescueStatusEnum.Resolved)
    )
    rescues = db.scalar(rescues_q) or 0

    # Adoptions DISTINCT pets with a Completed adoption
    adoptions_q = (
        select(func.count(func.distinct(AdoptionRequest.pet_id)))
        .where(AdoptionRequest.status == AdoptionStatus.Completed)
    )
    adoptions = db.scalar(adoptions_q) or 0

    # Located stray map entries of type 'stray_animal'
    located_q = (
        select(func.count())
        .select_from(StrayMapEntry)
        .where(StrayMapEntry.location_type == LocationType.stray_animal)
    )
    located = db.scalar(located_q) or 0

    return StatsOut(rescues=rescues, adoptions=adoptions, located=located)
