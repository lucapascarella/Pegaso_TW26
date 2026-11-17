import uuid
from typing import Annotated

import jwt
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from modules.Exceptions import CustomException
from modules.database import get_session
from modules.models.user import UserRole, UserSql
from modules.security import decode_access_token

# Shortcut used by the routers: "session: SessionDep"
SessionDep = Annotated[Session, Depends(get_session)]

# Reads the "Authorization: Bearer <token>" header; tokenUrl enables the Authorize button in /docs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def get_current_user(session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]) -> UserSql:
    """Authentication: who is calling? 401 if the token is missing, invalid or expired."""
    unauthorized = CustomException("Invalid or expired token.", None, status.HTTP_401_UNAUTHORIZED)
    try:
        payload = decode_access_token(token)
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise unauthorized

    user = session.get(UserSql, user_id)
    if user is None or user.disabled:
        raise unauthorized
    return user


UserDep = Annotated[UserSql, Depends(get_current_user)]


def require_role(*roles: UserRole):
    """Authorization: may this user do it? 403 if the role is not allowed."""
    def checker(user: UserDep) -> UserSql:
        if user.role not in roles:
            raise CustomException("Operation not allowed for your role.", {"role": user.role}, status.HTTP_403_FORBIDDEN)
        return user
    return checker


AdminDep = Annotated[UserSql, Depends(require_role(UserRole.Admin))]
EditorDep = Annotated[UserSql, Depends(require_role(UserRole.Admin, UserRole.Operator))]
