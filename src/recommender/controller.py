

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database.core import get_db
from ..auth.service import CurrentUser
from ..entities.user import User
from .service import get_recommended_pets
from ..recommender.models import PetResponse

router = APIRouter(prefix="/recommend", tags=["Recommendation"])


@router.get("/", response_model=Dict[str, Any])
def recommend_pets_for_user(
    current_user: CurrentUser,
    top_k: int = 5,
    db: Session = Depends(get_db),
):
    # 1Get UUID from token
    user_uuid = current_user.get_uuid()
    if user_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing user in token",
        )

    # Confirm user exists in DB
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found with ID: {user_uuid}",
        )

    # Use UUID when calling service
    try:
        results = get_recommended_pets(db, user_uuid, top_k)
        pet_list = [PetResponse(**pet) for pet in results]

        return {
            "user_id": str(user_uuid),
            "recommendations": pet_list,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


