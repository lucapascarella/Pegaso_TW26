import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field as PydField
from sqlmodel import Field, SQLModel

from modules.models.device import utc_now
from modules.models.models import ResponseGeneric


class UserRole(str, Enum):
    Admin = "admin"        # manages users and devices
    Operator = "operator"  # changes device configurations
    Viewer = "viewer"      # read only


# ---------- Tables ----------
class UserSql(SQLModel, table=True):
    __tablename__ = "app_user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=128)
    full_name: str = Field(max_length=64)
    role: UserRole = UserRole.Viewer
    hashed_password: str          # never the plain password
    disabled: bool = False
    created_at: datetime = Field(default_factory=utc_now)


# ---------- Requests ----------
class ReqUserCreate(BaseModel):
    email: EmailStr
    full_name: str = PydField(min_length=1, max_length=64)
    password: str = PydField(min_length=10, max_length=128)
    role: UserRole = UserRole.Viewer


# ---------- Responses ----------
class UserShort(BaseModel):
    """User as returned by the API: no password hash."""
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    disabled: bool
    created_at: datetime


class Token(BaseModel):
    """OAuth2 token response: field names are fixed by the standard."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class RespUserDetails(ResponseGeneric):
    data: UserShort | None = None


class RespUserList(ResponseGeneric):
    data: list[UserShort] = []
