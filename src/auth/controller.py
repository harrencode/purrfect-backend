

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..database.core import DbSession
from ..rate_limiter import limiter
from . import models, service
from .service import SECRET_KEY, ALGORITHM, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from src.entities.user import User
from src.auth.verification import hash_code, generate_code

from src.utils.ses_service import send_verification_code
import os

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

VERIFY_CODE_TTL_MIN = int(os.getenv("VERIFY_CODE_TTL_MIN", "10"))
# Register new user
from fastapi import File, UploadFile, Form
from ..entities.user import PreferredSpeciesEnum, PreferredSizeEnum, TemperamentEnum, ActivityLevelEnum


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
async def register_user(
    request: Request,
    db: DbSession,
    email: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    password: str = Form(...),
    preferred_species: PreferredSpeciesEnum = Form(PreferredSpeciesEnum.Any),
    preferred_size: PreferredSizeEnum = Form(PreferredSizeEnum.Any),
    temperament: TemperamentEnum = Form(TemperamentEnum.Any),
    activity_level: ActivityLevelEnum = Form(ActivityLevelEnum.Any),
    min_age: int | None = Form(None),
    max_age: int | None = Form(None),
    profile_photo: UploadFile | None = File(None)
):
    return service.register_user(
        db,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        preferred_species=preferred_species,
        preferred_size=preferred_size,
        temperament=temperament,
        activity_level=activity_level,
        min_age=min_age,
        max_age=max_age,
        profile_photo=profile_photo
    )








# @router.post("/", status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/hour")
# async def register_user(
#     request: Request,
#     db: DbSession,
#     register_user_request: models.RegisterUserRequest
# ):
#     service.register_user(db, register_user_request)
#     return {"message": "User registered successfully"}


# Login to get JWT token
@router.post("/token", response_model=models.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession
):
    return service.login_for_access_token(form_data, db)

from fastapi import Form

# @router.post("/token", response_model=models.Token)
# async def login_for_access_token(
#     db: DbSession,
#     username: str = Form(...),
#     password: str = Form(...),
#     latitude: float | None = Form(None),
#     longitude: float | None = Form(None),
# ):
#     """
#     Custom login route that also accepts user's current latitude/longitude.
#     Used by frontend SignIn form to generate nearby notifications.
#     """
#     from src.auth import service
#     return service.login_for_access_token_with_location(db, username, password, latitude, longitude)



# Verify token endpoint (for frontend calls like /auth/verify)
@router.post("/verify")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        return {"valid": True, "user_id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")



@router.post("/verify-code", response_model=models.Token)
def verify_code_and_login(body: models.VerifyCodeRequest, db: DbSession):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or code")

    if user.is_email_verified and user.is_active:
        token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return models.Token(access_token=token, token_type="bearer")

    if not user.email_verification_expires_at or user.email_verification_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code expired. Please request a new code.")

    if user.email_verification_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Please request a new code.")

    if hash_code(body.code) != user.email_verification_token:
        user.email_verification_attempts += 1
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid email or code")

    # success
    user.is_email_verified = True
    user.is_active = True
    user.email_verification_token = None
    user.email_verification_expires_at = None
    user.email_verification_attempts = 0
    db.commit()

    token = create_access_token(user, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return models.Token(access_token=token, token_type="bearer")

@router.post("/resend-code")
@limiter.limit("5/hour")
def resend_code(request: Request, body: models.ResendCodeRequest, db: DbSession):
    user = db.query(User).filter(User.email == body.email).first()

    # Always return success message to avoid email enumeration
    if not user:
        return {"message": "If the email exists, a new code has been sent."}

    if user.is_email_verified:
        return {"message": "Email already verified. Please sign in."}

    code = generate_code()
    user.email_verification_token = hash_code(code)
    user.email_verification_expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFY_CODE_TTL_MIN)
    user.email_verification_attempts = 0
    user.is_active = False
    db.commit()

    send_verification_code(user.email, code)

    return {"message": "A new verification code has been sent."}