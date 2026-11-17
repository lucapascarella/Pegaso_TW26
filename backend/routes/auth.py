from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from modules.Exceptions import CustomException
from modules.crud import user as crud
from modules.dependencies import SessionDep, UserDep
from modules.models.user import RespUserDetails, Token, UserShort
from modules.security import create_access_token

router = APIRouter(tags=["Auth"])


@router.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    """
    OAuth2 password flow: username (the email) and password as form fields
    """
    user = crud.authenticate(session, form.username, form.password)
    if user is None:
        raise CustomException("Wrong email or password.", None, status.HTTP_401_UNAUTHORIZED)

    token, expires_in = create_access_token(user.id, user.role.value)
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me")
def read_me(user: UserDep) -> RespUserDetails:
    """
    The user who owns the token
    """
    return RespUserDetails(data=UserShort.model_validate(user, from_attributes=True))
