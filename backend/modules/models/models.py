from typing import Any

from pydantic import BaseModel


class ResponseGeneric(BaseModel):
    """Common envelope for every API response."""
    success: bool = True
    message: str | None = None
    data: Any | None = None
    details: Any | None = None
