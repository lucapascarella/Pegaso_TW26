import logging

from fastapi import status
from sqlmodel import Session, select

from modules.Exceptions import CustomException
from modules.models.user import ReqUserCreate, UserRole, UserSql
from modules.security import hash_password, verify_password
from utils.settings import settings

logger = logging.getLogger(__name__)


def get_user_by_email(session: Session, email: str) -> UserSql | None:
    return session.exec(select(UserSql).where(UserSql.email == email.lower())).first()


def list_users(session: Session) -> list[UserSql]:
    return list(session.exec(select(UserSql).order_by(UserSql.email)).all())


def create_user(session: Session, req: ReqUserCreate) -> UserSql:
    if get_user_by_email(session, req.email):
        raise CustomException(f"User {req.email} already exists.", None, status.HTTP_409_CONFLICT)

    user = UserSql(email=req.email.lower(), full_name=req.full_name, role=req.role,
                   hashed_password=hash_password(req.password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, email: str, password: str) -> UserSql | None:
    """Return the user if email and password are correct, otherwise None."""
    user = get_user_by_email(session, email)
    if user is None or user.disabled or not verify_password(password, user.hashed_password):
        return None
    return user


def ensure_admin(session: Session) -> None:
    """Create the first administrator from the settings when the user table is empty."""
    if session.exec(select(UserSql)).first() is None:
        session.add(UserSql(email=settings.ADMIN_EMAIL.lower(), full_name="Administrator", role=UserRole.Admin,
                            hashed_password=hash_password(settings.ADMIN_PASSWORD)))
        session.commit()
        logger.warning("Created first admin user %s: change its password!", settings.ADMIN_EMAIL)
