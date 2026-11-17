from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from modules.Exceptions import CustomException
from modules.crud.user import ensure_admin
from modules.database import create_db_and_tables, engine
from modules.models.models import ResponseGeneric
from routes import auth, devices, users
from utils.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Code executed once at startup (before yield) and once at shutdown (after yield)."""
    create_db_and_tables()
    with Session(engine) as session:
        ensure_admin(session)
    yield


app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG, lifespan=lifespan)

# Routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(users.router, prefix="/api/users")
app.include_router(devices.router, prefix="/api/devices")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation errors (422) with the common response envelope."""
    msg = "Unprocessable input data, e.g., missing JSON field(s) or invalid path parameter(s)."
    body = ResponseGeneric(success=False, message=msg, details=exc.errors())
    return JSONResponse(jsonable_encoder(body), status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Framework errors (404 route not found, 401 missing token...) with the common envelope."""
    body = ResponseGeneric(success=False, message=str(exc.detail))
    return JSONResponse(jsonable_encoder(body), exc.status_code, headers=getattr(exc, "headers", None))


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    return JSONResponse(exc.json, exc.status_code)


@app.get("/")
def root() -> ResponseGeneric:
    """Health check: the API is up and running."""
    return ResponseGeneric(message=f"{settings.APP_NAME} is running")
