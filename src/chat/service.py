from uuid import uuid4, UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.entities.chat import Chat, ChatMember, ChatMessage
from src.auth.models import TokenData
from src.exceptions import ChatNotFoundError, ChatMemberExistsError
from sqlalchemy.orm import Session
from ..entities.chat import Chat, ChatMember, ChatTypeEnum
import uuid

def create_chat(db: Session, current_user, chat_type: ChatTypeEnum, related_entity_id: uuid.UUID):
    # Check if chat already exists for this entity
    existing_chat = (
        db.query(Chat)
        .filter(Chat.chat_type == chat_type)
        .filter(Chat.related_entity_id == related_entity_id)
        .first()
    )

    if existing_chat:
        # Ensure current user is a member
        already_member = any(m.user_id == current_user.get_uuid() for m in existing_chat.members)
        if not already_member:
            db.add(ChatMember(chat_id=existing_chat.chat_id, user_id=current_user.get_uuid()))
            db.commit()
        return existing_chat

    # Otherwise create new chat
    new_chat = Chat(
        chat_type=chat_type,
        related_entity_id=related_entity_id,
        creator_id=current_user.get_uuid()
    )
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    # Add creator as member
    db.add(ChatMember(chat_id=new_chat.chat_id, user_id=current_user.get_uuid()))
    db.commit()

    return new_chat

def add_member_to_chat(db: Session, chat_id: UUID, user_id: UUID):
    chat = db.query(Chat).filter(Chat.chat_id == chat_id).first()
    if not chat:
        raise ChatNotFoundError(chat_id)
    existing = db.query(ChatMember).filter(ChatMember.chat_id == chat_id, ChatMember.user_id == user_id).first()
    if existing:
        raise ChatMemberExistsError()
    member = ChatMember(chat_id=chat_id, user_id=user_id)
    db.add(member)
    db.commit()
    return member

def post_message(db: Session, chat_id: UUID, sender_id: UUID, content: str):
    message = ChatMessage(chat_id=chat_id, sender_id=sender_id, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_chat_messages(db: Session, chat_id: UUID, limit=100):
    return db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at.asc()).limit(limit).all()
