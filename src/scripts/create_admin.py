import os
from uuid import uuid4

from passlib.context import CryptContext

from src.database.core import SessionLocal
from src.entities.user import User


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")
    first_name = os.getenv("ADMIN_FIRST_NAME", "Admin")
    last_name = os.getenv("ADMIN_LAST_NAME", "User")
    reset_password = _get_bool("ADMIN_RESET_PASSWORD", False)

    if not email or not password:
        print("ADMIN_EMAIL or ADMIN_PASSWORD not set; skipping admin seed.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if user:
            user.is_admin = True
            user.is_active = True
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_expires_at = None
            user.email_verification_attempts = 0

            if reset_password:
                user.password_hash = bcrypt_context.hash(password)

            db.commit()
            print(f"Admin user already exists and is enabled: {email}")
            return

        admin = User(
            id=uuid4(),
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=bcrypt_context.hash(password),
            is_admin=True,
            is_active=True,
            is_email_verified=True,
            email_verification_token=None,
            email_verification_expires_at=None,
            email_verification_attempts=0,
        )

        db.add(admin)
        db.commit()
        print(f"Admin user created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
