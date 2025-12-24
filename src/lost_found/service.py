from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from . import models
from src.entities.lost_found import LostFoundReport, LostFoundStatusEnum
from src.entities.chat import Chat, ChatMember, ChatTypeEnum
from src.entities.leaderboard import LeaderboardUser
from src.exceptions import LostFoundCreationError, LostFoundNotFoundError, AuthorizationError
import logging
from math import radians, sin, cos, sqrt, atan2


def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def create_lost_pet_report(current_user, db: Session, payload: models.LostFoundCreate) -> models.LostFoundResponse:
    try:
        report = LostFoundReport(**payload.model_dump(exclude={"chat_id"}))
        report.report_id = uuid4()
        report.user_id = current_user.get_uuid()
        report.created_at = datetime.now(timezone.utc)
        report.updated_at = datetime.now(timezone.utc)

        # Create chat
        chat = Chat(
            chat_type=ChatTypeEnum.LostPet,
            related_entity_id=report.report_id,
            creator_id=current_user.get_uuid(),
        )
        db.add(chat)
        db.flush()
        db.add(ChatMember(chat_id=chat.chat_id, user_id=current_user.get_uuid()))
        report.chat_id = chat.chat_id

        db.add(report)
        db.commit()
        db.refresh(report)

        # Update leaderboard
        user_id = current_user.get_uuid()
        entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == user_id).first()
        if entry:
            entry.score += 5
            entry.lost_pets += 1
            entry.last_active = datetime.now().isoformat()
        else:
            db.add(
                LeaderboardUser(
                    user_id=user_id,
                    score=5,
                    lost_pets=1,
                    last_active=datetime.now().isoformat(),
                )
            )
        db.commit()

        return models.LostFoundResponse(
            reportId=report.report_id,
            userId=report.user_id,
            pet_name=report.pet_name,
            pet_type=report.pet_type,
            gender=report.gender.value if hasattr(report.gender, "value") else report.gender,
            description=report.description,
            location=report.location,
            latitude=report.latitude,
            longitude=report.longitude,
            photo=report.photo,
            status=report.status.value if hasattr(report.status, "value") else report.status,
            chatId=report.chat_id,
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create lost pet report: {str(e)}")
        raise LostFoundCreationError(str(e))


def get_lost_pets(current_user, db: Session):
    reports = db.query(LostFoundReport).options(joinedload(LostFoundReport.user)).all()
    results = []
    for r in reports:
        u = r.user
        results.append({
            "reportId": r.report_id,
            "userId": r.user_id,
            "userFirstName": u.first_name if u else "Unknown",
            "userLastName": u.last_name if u else "Unknown",
            "userFullName": f"{u.first_name} {u.last_name}" if u else "Unknown",
            "pet_name": r.pet_name,
            "pet_type": r.pet_type,
            "gender": r.gender.value if hasattr(r.gender, "value") else r.gender,
            "description": r.description,
            "location": r.location,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "photo": r.photo,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "chatId": r.chat_id
        })
    return results


def get_lost_pet_by_id(current_user, db: Session, report_id: UUID):
    report = db.query(LostFoundReport).filter(LostFoundReport.report_id == report_id).first()
    if not report:
        raise LostFoundNotFoundError(report_id)
    return report


def update_lost_pet(current_user, db: Session, report_id: UUID, payload: models.LostFoundUpdate):
    report = db.query(LostFoundReport).filter(LostFoundReport.report_id == report_id).first()
    if not report:
        raise LostFoundNotFoundError(report_id)

    update_data = payload.model_dump(exclude_unset=True)
    db.query(LostFoundReport).filter(LostFoundReport.report_id == report_id).update(update_data)
    db.commit()
    db.refresh(report)

    # Return the same response format as LostFoundResponse
    u = report.user
    return models.LostFoundResponse(
        reportId=report.report_id,
        userId=report.user_id,
        userFirstName=u.first_name if u else "Unknown",
        userLastName=u.last_name if u else "Unknown",
        userFullName=f"{u.first_name} {u.last_name}" if u else "Unknown",
        pet_name=report.pet_name,
        pet_type=report.pet_type,
        gender=report.gender.value if hasattr(report.gender, "value") else report.gender,
        description=report.description,
        location=report.location,
        latitude=report.latitude,
        longitude=report.longitude,
        photo=report.photo,
        status=report.status.value if hasattr(report.status, "value") else report.status,
        chatId=report.chat_id,
    )



def delete_lost_pet(current_user, db: Session, report_id: UUID):
    report = db.query(LostFoundReport).filter(LostFoundReport.report_id == report_id).first()
    if not report:
        raise LostFoundNotFoundError(report_id)
    db.delete(report)
    db.commit()


from sqlalchemy.orm import joinedload

def get_lost_pet_by_chat(current_user, db: Session, chat_id: UUID):
    report = (
        db.query(LostFoundReport)
        .options(joinedload(LostFoundReport.user))
        .filter(LostFoundReport.chat_id == chat_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Lost pet not found for this chat")

    u = report.user

    return models.LostFoundResponse(
        reportId=report.report_id,
        userId=report.user_id,
        userFirstName=u.first_name if u else "Unknown",
        userLastName=u.last_name if u else "Unknown",
        userFullName=f"{u.first_name} {u.last_name}" if u else "Unknown",
        pet_name=report.pet_name,
        pet_type=report.pet_type,
        gender=report.gender.value if hasattr(report.gender, "value") else report.gender,
        description=report.description,
        location=report.location,
        latitude=report.latitude,
        longitude=report.longitude,
        photo=report.photo,
        status=report.status.value if hasattr(report.status, "value") else report.status,
        chatId=report.chat_id,
    )



def get_nearby_lost_pets(current_user, db: Session, lat: float, lon: float, radius_km: float):
    reports = db.query(LostFoundReport).filter(LostFoundReport.latitude.isnot(None), LostFoundReport.longitude.isnot(None)).all()

    nearby = [
        r for r in reports
        if haversine(lat, lon, r.latitude, r.longitude) <= radius_km
    ]

    return [
        models.LostFoundResponse(
            reportId=r.report_id,
            userId=r.user_id,
            pet_name=r.pet_name,
            pet_type=r.pet_type,
            gender=r.gender.value if hasattr(r.gender, "value") else r.gender,
            description=r.description,
            location=r.location,
            latitude=r.latitude,
            longitude=r.longitude,
            photo=r.photo,
            status=r.status.value if hasattr(r.status, "value") else r.status,
            chatId=r.chat_id
        )
        for r in nearby
    ]
