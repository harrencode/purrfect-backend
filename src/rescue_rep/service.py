

from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from . import models
from src.auth.models import TokenData
from src.entities.rescue_rep import RescueReport, RescueStatusEnum
from src.entities.chat import Chat, ChatTypeEnum, ChatMember
from src.exceptions import (
    RescueReportCreationError,
    RescueReportNotFoundError,
    AuthorizationError
)
from sqlalchemy.orm import joinedload
from sqlalchemy import func
from src.entities.chat import ChatMessage
from src.entities.leaderboard import LeaderboardUser
from math import radians, sin, cos, sqrt, atan2

import logging



def create_rescue_report(
    current_user: TokenData,
    db: Session,
    rescue_report: models.RescueReportCreate
) -> models.RescueReportResponse:
    try:
        new_report = RescueReport(**rescue_report.model_dump(exclude={"chat_id"}))
        new_report.report_id = uuid4()
        new_report.user_id = current_user.get_uuid()
        new_report.created_at = datetime.now(timezone.utc)
        new_report.updated_at = datetime.now(timezone.utc)

        # Create a chat for this rescue
        chat = Chat(
            chat_type=ChatTypeEnum.Rescue,
            related_entity_id=new_report.report_id,
            creator_id=current_user.get_uuid()
        )
        db.add(chat)
        db.flush()
        member = ChatMember(chat_id=chat.chat_id, user_id=current_user.get_uuid())
        db.add(member)
        new_report.chat_id = chat.chat_id

        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # Leaderboard update
        user_id = current_user.get_uuid()
        leaderboard = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == user_id).first()
        if leaderboard:
            leaderboard.score += 10
            leaderboard.rescues += 1
            leaderboard.last_active = datetime.now().isoformat()
        else:
            db.add(
                LeaderboardUser(
                    user_id=user_id,
                    score=10,
                    rescues=1,
                    last_active=datetime.now().isoformat(),
                )
            )
        db.commit()

        logging.info(f"Created rescue report {new_report.report_id} by user {user_id}")
        return models.RescueReportResponse(
            reportId=new_report.report_id,
            userId=new_report.user_id,
            location=new_report.location,
            photo=new_report.photo,
            status=new_report.status.value if hasattr(new_report.status, 'value') else new_report.status,
            alert_type=new_report.alert_type.value if hasattr(new_report.alert_type, 'value') else new_report.alert_type,
            description=new_report.description,
            chat_id=new_report.chat_id
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Failed to create rescue report for user {current_user.get_uuid()}. Error: {str(e)}")
        raise RescueReportCreationError(str(e))



def get_rescue_report_by_id(
    current_user: TokenData,
    db: Session,
    report_id: UUID
) -> models.RescueReportResponse:
    report = db.query(RescueReport).filter(
        RescueReport.report_id == report_id,
        RescueReport.user_id == current_user.get_uuid()
    ).first()

    if not report:
        logging.warning(f"Rescue report {report_id} not found for user {current_user.get_uuid()}")
        raise RescueReportNotFoundError(report_id)

    logging.info(f"Retrieved rescue report {report_id} for user {current_user.get_uuid()}")

    return models.RescueReportResponse(
        reportId=report.report_id,
        # petId=report.pet_id,
        userId=report.user_id,
        location=report.location,
        photo=report.photo,
        status=report.status,
        alert_type=report.alert_type,
        description=report.description
    )




def get_rescue_reports(current_user, db: Session):
    # Fetch all rescue reports with user info
    reports = db.query(RescueReport).options(joinedload(RescueReport.user)).all()

    results = []
    for r in reports:
        user = r.user
        results.append({
            "reportId": r.report_id,
            "userId": r.user_id,
            "userFirstName": user.first_name if user else "Unknown",
            "userLastName": user.last_name if user else "Unknown",
            "userFullName": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "location": r.location,
            "latitude": r.latitude,
            "longitude": r.longitude,
            "photo": r.photo,
            "status": r.status.value if hasattr(r.status, "value") else r.status,
            "alert_type": r.alert_type.value if hasattr(r.alert_type, "value") else r.alert_type,
            "description": r.description,
            "chatId": r.chat_id
        })
    return results










def update_rescue_report(
    current_user: TokenData,
    db: Session,
    report_id: UUID,
    rescue_report_update: models.RescueReportUpdate
) -> models.RescueReportResponse:
    report = db.query(RescueReport).filter(RescueReport.report_id == report_id).first()
    if not report:
        raise RescueReportNotFoundError(report_id)

    # Ensure only the owner can mark as resolved
    if rescue_report_update.status is not None:
        new_status = rescue_report_update.status
        if new_status == RescueStatusEnum.Resolved.value and report.user_id != current_user.get_uuid():
            raise AuthorizationError("Only the creator can mark the rescue as complete")

    update_data = rescue_report_update.model_dump(exclude_unset=True)
    db.query(RescueReport).filter(
        RescueReport.report_id == report_id,
        RescueReport.user_id == report.user_id
    ).update(update_data)
    db.commit()

    # Reward participants when marked as resolved
    if "status" in update_data and update_data["status"] == RescueStatusEnum.Resolved.value:
        logging.info(f"Rescue {report_id} marked as resolved. Awarding points...")

        if report.chat_id:
            # Count messages per user
            message_counts = (
                db.query(ChatMessage.sender_id, func.count(ChatMessage.message_id))
                .filter(ChatMessage.chat_id == report.chat_id)
                .group_by(ChatMessage.sender_id)
                .all()
            )

            for sender_id, msg_count in message_counts:
                points = 2 * msg_count  # 2 pts per message
                entry = db.query(LeaderboardUser).filter(LeaderboardUser.user_id == sender_id).first()
                if entry:
                    entry.score += points
                    entry.last_active = datetime.now().isoformat()
                else:
                    db.add(
                        LeaderboardUser(
                            user_id=sender_id,
                            score=points,
                            last_active=datetime.now().isoformat(),
                        )
                    )
            db.commit()

    logging.info(f"Updated rescue report {report_id} by user {current_user.get_uuid()}")
    return get_rescue_report_by_id(current_user, db, report_id)




def get_rescue_report_by_chat(current_user, db: Session, chat_id: UUID) -> models.RescueReportResponse:
    report = db.query(RescueReport).filter(RescueReport.chat_id == chat_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rescue report not found for this chat")
    
    

    return models.RescueReportResponse(
        reportId=report.report_id,
        userId=report.user_id,
        userFirstName=report.user.first_name if report.user else "Unknown",
        userLastName=report.user.last_name if report.user else "Unknown",
        userFullName=f"{report.user.first_name} {report.user.last_name}" if report.user else "Unknown",
        location=report.location,
        photo=report.photo,
        status=report.status.value if hasattr(report.status, "value") else report.status,
        alert_type=report.alert_type.value if hasattr(report.alert_type, "value") else report.alert_type,
        description=report.description,
        chatId=report.chat_id
    )





def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_nearby_rescue_reports(current_user, db: Session, lat: float, lon: float, radius_km: float):
    reports = db.query(RescueReport).filter(RescueReport.latitude.isnot(None), RescueReport.longitude.isnot(None)).all()

    nearby = [
        r for r in reports
        if haversine(lat, lon, r.latitude, r.longitude) <= radius_km
    ]

    return [
        models.RescueReportResponse(
            reportId=r.report_id,
            userId=r.user_id,
            location=r.location,
            latitude=r.latitude,
            longitude=r.longitude,
            photo=r.photo,
            status=r.status.value if hasattr(r.status, "value") else r.status,
            alert_type=r.alert_type.value if hasattr(r.alert_type, "value") else r.alert_type,
            description=r.description,
            chatId=r.chat_id
        )
        for r in nearby
    ]
