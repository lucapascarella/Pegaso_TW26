from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from modules.database import get_session

# Shortcut used by the routers: "session: SessionDep"
SessionDep = Annotated[Session, Depends(get_session)]
