from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.auth.models import TokenData
from ..entities.adoption_req import AdoptionRequest, AdoptionStatus
from ..entities.pet import Pet
from src.entities.leaderboard import LeaderboardUser  
from sqlalchemy import and_
from sqlalchemy import func
from src.entities.leaderboard import LeaderboardUser
from src.entities.chat import ChatMessage
import logging
from datetime import datetime, timezone


import logging



def create_adoption_request(
    current_user: TokenData,
    db: Session,
    adoption_req: models.AdoptionRequestCreate
) -> models.AdoptionRequestResponse:
    try:
        # Create Pet
        pet_data = adoption_req.pet.model_dump(exclude={"images"})
        new_pet = Pet(**pet_data)
        new_pet.pet_id = uuid4()
        new_pet.user_id = current_user.get_uuid()
        new_pet.created_at = datetime.now(timezone.utc)
        new_pet.updated_at = datetime.now(timezone.utc)
        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)

        # Create Adoption Request
        new_request = AdoptionRequest(
            adopt_id=uuid4(),
            pet_id=new_pet.pet_id,
            requester_id=current_user.get_uuid(),
            description=adoption_req.description,
            status=AdoptionStatus.Pending,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        # Update Leaderboard (+10 points for new adoption request)
        try:
            user_id = current_user.get_uuid()
            entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == user_id).first()
            now_str = datetime.now(timezone.utc).isoformat()

            if entry:
                entry.score += 10
                entry.adoptions += 1
                entry.last_active = now_str
            else:
                entry = LeaderboardUser(
                    user_id=user_id,
                    score=10,
                    adoptions=1,
                    last_active=now_str,
                    rescues=0,
                    lost_pets=0,
                    map_contributions=0,
                )
                db.add(entry)
            db.commit()
            logging.info(f"Leaderboard updated for user {user_id}: +10 points (adoption request)")
        except Exception as e:
            logging.error(f"Leaderboard update failed: {e}")

        return models.AdoptionRequestResponse(
            id=str(new_request.adopt_id),
            pet=models.PetResponse.from_orm(new_pet),
            requester_id=str(new_request.requester_id),
            description=new_request.description,
            status=new_request.status.value,
            created_at=new_request.created_at,
            updated_at=new_request.updated_at
        )

    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create adoption request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



def get_adoption_requests(current_user: TokenData, db: Session) -> list[models.AdoptionRequestResponse]:
    requests = db.query(AdoptionRequest).filter(AdoptionRequest.requester_id == current_user.get_uuid()).all()
    response = []
    for r in requests:
        pet = db.query(Pet).filter(Pet.pet_id == r.pet_id).first()
        response.append(models.AdoptionRequestResponse(
            id=str(r.adopt_id),
            pet=models.PetResponse.from_orm(pet),
            requester_id=str(r.requester_id),
            description=r.description,
            status=r.status.value,
            created_at=r.created_at,
            updated_at=r.updated_at
        ))
    return response


def get_adoption_request_by_id(current_user: TokenData, db: Session, adopt_id: UUID) -> models.AdoptionRequestResponse:
    req = db.query(AdoptionRequest).filter(AdoptionRequest.adopt_id == adopt_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Adoption request not found")
    pet = db.query(Pet).filter(Pet.pet_id == req.pet_id).first()
    return models.AdoptionRequestResponse(
        id=str(req.adopt_id),
        pet=models.PetResponse.from_orm(pet),
        requester_id=str(req.requester_id),
        description=req.description,
        status=req.status.value,
        created_at=req.created_at,
        updated_at=req.updated_at
    )





def update_adoption_request(
    current_user: TokenData,
    db: Session,
    adopt_id: UUID,
    adoption_req_update: models.AdoptionRequestUpdate,
    owner_id: UUID = None
) -> models.AdoptionRequestResponse:
    req = db.query(AdoptionRequest).filter(AdoptionRequest.adopt_id == adopt_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Adoption request not found")

    update_data = adoption_req_update.model_dump(exclude_unset=True)

    # Save chat link if provided
    if "chat_id" in update_data:
        req.chat_id = update_data["chat_id"]

    # Only requester can edit description
    if "description" in update_data and req.requester_id != current_user.get_uuid():
        raise HTTPException(status_code=403, detail="Not allowed to update description")
    if "description" in update_data:
        req.description = update_data["description"]

    # Load the pet once (we also need the owner check)
    pet = db.query(Pet).filter(Pet.pet_id == req.pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")

    # Only pet owner can change status
    if "status" in update_data:
        if current_user.get_uuid() != pet.user_id:
            raise HTTPException(status_code=403, detail="Only pet owner can change status")

        # Parse/validate status
        try:
            req.status = AdoptionStatus(update_data["status"])
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status value")

    
    # If the request is (now) Approved or Completed, ensure the pet is marked adopted,
    # even if 'status' wasn't in this update payload
    should_mark_adopted = req.status in (AdoptionStatus.Approved, AdoptionStatus.Completed)
    pet_is_already_adopted = bool(pet.is_adopted)

    # Always bump req.updated_at
    now_utc = datetime.now(timezone.utc)
    req.updated_at = now_utc

    if should_mark_adopted and not pet_is_already_adopted:
        # Force a DB-level update so the change always persists
        db.query(Pet).filter(Pet.pet_id == req.pet_id).update(
            {"is_adopted": True, "updated_at": now_utc},
            synchronize_session=False
        )

        # Persist request + pet together
        db.add(req)
        db.commit()
        # Re-load pet to reflect the new DB state
        pet = db.query(Pet).filter(Pet.pet_id == req.pet_id).first()

        # Leaderboard update (separate transaction so failure doesn't undo adoption)
        try:
            if req.chat_id:
                POINTS_PER_MESSAGE = 1
                user_message_counts = (
                    db.query(ChatMessage.sender_id, func.count(ChatMessage.message_id).label("msg_count"))
                    .filter(ChatMessage.chat_id == req.chat_id)
                    .group_by(ChatMessage.sender_id)
                    .all()
                )
                for sender_id, msg_count in user_message_counts:
                    points = int(msg_count) * POINTS_PER_MESSAGE
                    entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == sender_id).first()
                    now_str = now_utc.isoformat()
                    if entry:
                        entry.score += points
                        entry.adoptions = (entry.adoptions or 0) + 1
                        entry.last_active = now_str
                    else:
                        db.add(
                            LeaderboardUser(
                                user_id=sender_id,
                                score=points,
                                rescues=0,
                                adoptions=1,
                                lost_pets=0,
                                map_contributions=0,
                                avatar=None,
                                last_active=now_str,
                            )
                        )
                db.commit()
        except Exception as e:
            db.rollback()
            # We intentionally do NOT raise adoption already persisted.
            logging.error(f"Leaderboard update failed for adoption {req.adopt_id}: {e}")
    else:
        # No adoption change necessary; just persist the request updates
        db.add(req)
        db.commit()

    # Build response with fresh pet state
    pet = db.query(Pet).filter(Pet.pet_id == req.pet_id).first()
    return models.AdoptionRequestResponse(
        id=str(req.adopt_id),
        pet=models.PetResponse.from_orm(pet),
        requester_id=str(req.requester_id),
        description=req.description,
        status=req.status.value,
        chat_id=str(req.chat_id) if req.chat_id else None,
        created_at=req.created_at,
        updated_at=req.updated_at,
    )




def delete_adoption_request(current_user: TokenData, db: Session, adopt_id: UUID):
    req = db.query(AdoptionRequest).filter(AdoptionRequest.adopt_id == adopt_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Adoption request not found")
    db.delete(req)
    db.commit()
    logging.info(f"Adoption request {adopt_id} deleted")
    return

def get_adoption_request_by_chat(current_user, db: Session, chat_id: UUID) -> models.AdoptionRequestResponse:
    req = db.query(AdoptionRequest).filter(AdoptionRequest.chat_id == chat_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Adoption request not found for this chat")

    pet = db.query(Pet).filter(Pet.pet_id == req.pet_id).first()

    return models.AdoptionRequestResponse(
        id=str(req.adopt_id),
        pet=models.PetResponse.from_orm(pet),
        requester_id=str(req.requester_id),
        description=req.description,
        status=req.status.value,
        chat_id=str(req.chat_id) if req.chat_id else None,
        created_at=req.created_at,
        updated_at=req.updated_at
    )


def get_all_adoption_requests(
    db: Session,
    exclude_user_id: str | None = None
) -> list[models.AdoptionRequestResponse]:
    """Return all adoption requests, excluding current user's pets and requests."""
    query = (
        db.query(AdoptionRequest)
        .join(Pet, AdoptionRequest.pet_id == Pet.pet_id)
        .filter(Pet.is_adopted == False)  # only available pets
    )

    if exclude_user_id:
        query = query.filter(
            and_(
                # Pet.user_id != exclude_user_id,
                AdoptionRequest.requester_id != exclude_user_id
            )
        )

    requests = query.all()
    response = []

    for r in requests:
        pet = db.query(Pet).filter(Pet.pet_id == r.pet_id).first()
        if not pet:
            continue

        response.append(
            models.AdoptionRequestResponse(
                id=str(r.adopt_id),
                pet=models.PetResponse.from_orm(pet),
                requester_id=str(r.requester_id),
                description=r.description,
                status=r.status.value,
                created_at=r.created_at,
                updated_at=r.updated_at,
            )
        )

    return response