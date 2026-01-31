import os
from datetime import timedelta, datetime, timezone
from typing import Annotated
from uuid import UUID, uuid4
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from src.entities.user import User
from . import models
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..exceptions import AuthenticationError
import logging
from src.utils.ses_service import send_verification_code
from src.auth.verification import generate_code, hash_code

from src.utils.s3_service import upload_image_to_s3

# Authentication settings

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)


def authenticate_user(email: str, password: str, db: Session) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password_hash):
        logging.warning(f"Failed authentication attempt for email: {email}")
        return False
    return user

def create_access_token(user: User, expires_delta: timedelta) -> str:
    to_encode = {
        "sub": str(user.id),                    
        "email": user.email,                    
        "exp": datetime.now(timezone.utc) + expires_delta,
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)




def verify_token(token: str) -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        logging.info(f"Decoded JWT payload: {payload}")
        return models.TokenData(user_id=user_id)
    except JWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()






VERIFY_CODE_TTL_MIN = int(os.getenv("VERIFY_CODE_TTL_MIN", "10"))

def register_user(
    db: Session,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    preferred_species=None,
    preferred_size=None,
    temperament=None,
    activity_level=None,
    min_age=None,
    max_age=None,
    profile_photo=None
):
    try:
        # Upload photo (or fallback)
        if profile_photo:
            photo_url = upload_image_to_s3(profile_photo, folder="users")
        else:
            photo_url = "https://avatar.iran.liara.run/public/11" 

        # Generate verification code
        code = generate_code()
        code_hash = hash_code(code)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFY_CODE_TTL_MIN)

        user = User(
            id=uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=get_password_hash(password),

            preferred_species=preferred_species,
            preferred_size=preferred_size,
            temperament=temperament,
            activity_level=activity_level,
            min_age=min_age,
            max_age=max_age,

            profile_photo_url=photo_url,

            # verification state
            is_active=True,
            is_email_verified=False,
            email_verification_token=code_hash,
            email_verification_expires_at=expires_at,
            email_verification_attempts=0,
        )

        db.add(user)
        db.commit()

        # Send code by email
        send_verification_code(email, code)

        return {"message": "Account created. Verification code sent to email."}

    except Exception as e:
        logging.error(f"Failed to register user {email}: {str(e)}")
        raise

    
    
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]) -> models.TokenData:
    return verify_token(token)

CurrentUser = Annotated[models.TokenData, Depends(get_current_user)]


def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session,
) -> models.Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise AuthenticationError()

    # block if not verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "EMAIL_NOT_VERIFIED", "email": user.email}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACCOUNT_INACTIVE"}
        )

    token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return models.Token(access_token=token, token_type="bearer")
