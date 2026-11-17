from fastapi import status
from fastapi.encoders import jsonable_encoder

from modules.models.models import ResponseGeneric


class CustomException(Exception):
    """Application error rendered with the common ResponseGeneric envelope."""

    def __init__(self, msg: str, data: dict | None = None, code: int = status.HTTP_400_BAD_REQUEST):
        self.status_code = code
        self.json = jsonable_encoder(ResponseGeneric(success=False, message=msg, data=data))
