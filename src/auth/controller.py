

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..database.core import DbSession
from ..rate_limiter import limiter
from . import models, service
from .service import SECRET_KEY, ALGORITHM  # ensure these exist in your service file

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


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





