from fastapi import APIRouter, status

from modules.crud import user as crud
from modules.dependencies import AdminDep, SessionDep
from modules.models.user import ReqUserCreate, RespUserDetails, RespUserList, UserShort

router = APIRouter(tags=["User"])


@router.get("/list")
def get_user_list(session: SessionDep, _: AdminDep) -> RespUserList:
    """
    List users (admin only)
    """
    users = crud.list_users(session)
    return RespUserList(data=[UserShort.model_validate(u, from_attributes=True) for u in users])


@router.post("", status_code=status.HTTP_201_CREATED)
def add_user(req: ReqUserCreate, session: SessionDep, _: AdminDep) -> RespUserDetails:
    """
    Create a user with a role (admin only)
    """
    user = crud.create_user(session, req)
    return RespUserDetails(message="User created.", data=UserShort.model_validate(user, from_attributes=True))
