from fastapi import APIRouter, status, Query
from typing import List, Optional
from uuid import UUID

from ..database.core import DbSession
from ..auth.service import CurrentUser
from . import models, service

router = APIRouter(
    prefix="/stray-map",
    tags=["Stray Map"]
)

@router.post("/", response_model=models.StrayMapResponse, status_code=status.HTTP_201_CREATED)
def create_stray_entry(db: DbSession, entry: models.StrayMapCreate, current_user: CurrentUser):
    return service.create_entry(current_user, db, entry)


@router.get("/", response_model=List[models.StrayMapResponse])
def get_stray_entries(db: DbSession, location_type: Optional[str] = Query(None, description="Filter by type: rescue_home, stray_animal, vet_center")):
    return service.get_entries(db, location_type)


@router.get("/{entry_id}", response_model=models.StrayMapResponse)
def get_stray_entry_by_id(db: DbSession, entry_id: UUID):
    return service.get_entry_by_id(db, entry_id)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_stray_entry(db: DbSession, entry_id: UUID, current_user: CurrentUser):
    service.delete_entry(current_user, db, entry_id)
