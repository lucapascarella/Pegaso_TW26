from fastapi import FastAPI

from modules.models.models import ResponseGeneric
from utils.settings import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)


@app.get("/")
def root() -> ResponseGeneric:
    """Health check: the API is up and running."""
    return ResponseGeneric(message=f"{settings.APP_NAME} is running")
