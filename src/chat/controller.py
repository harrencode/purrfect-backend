from fastapi import APIRouter, Depends, status
from uuid import UUID
from ..database.core import DbSession
from . import service as chat_service
from src.auth.service import CurrentUser
from . import models as chat_models
from ..rescue_rep.models import RescueReportResponse
from ..exceptions import HTTPException
from src.entities.rescue_rep import RescueReport


router = APIRouter(prefix="/chats", tags=["Chats"])

@router.post("/", response_model=chat_models.ChatResponse)
def create_chat(db: DbSession, chat_create: chat_models.ChatCreate, current_user: CurrentUser):
    chat = chat_service.create_chat(
        db,
        current_user,
        chat_create.chat_type,
        chat_create.related_entity_id
    )
    return chat_models.ChatResponse(
        chatId=chat.chat_id,
        chat_type=chat.chat_type.value,
        related_entity_id=chat.related_entity_id,
        creator_id=chat.creator_id,
        members=[m.user_id for m in chat.members],
        created_at=chat.created_at
    )


@router.post("/{chat_id}/join", status_code=status.HTTP_200_OK)
def join_chat(chat_id: UUID, db: DbSession, current_user: CurrentUser):
    chat_service.add_member_to_chat(db, chat_id, current_user.get_uuid())
    return {"detail": "joined", "chatId": chat_id}

@router.get("/{chat_id}/messages")
def get_chat_messages(chat_id: UUID, db: DbSession):
    messages = chat_service.get_chat_messages(db, chat_id)
    return [
        {
            "messageId": str(m.message_id),
            "chatId": str(m.chat_id),
            "senderId": str(m.sender_id),
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]

@router.post("/{chat_id}/messages")
def post_message(chat_id: UUID, body: chat_models.ChatMessageCreate, db: DbSession, current_user: CurrentUser):
    msg = chat_service.post_message(db, chat_id, current_user.get_uuid(), body.content)
    return {
        "messageId": str(msg.message_id),
        "chatId": str(msg.chat_id),
        "senderId": str(msg.sender_id),
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }

@router.get("/by-chat/{chat_id}", response_model=RescueReportResponse)
def get_report_by_chat(chat_id: UUID, db: DbSession, current_user: CurrentUser):
    report = db.query(RescueReport).filter(RescueReport.chat_id == chat_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Rescue report not found")
    return report
