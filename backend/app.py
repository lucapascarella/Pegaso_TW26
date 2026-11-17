from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from modules.Exceptions import CustomException
from modules.models.models import ResponseGeneric
from routes import devices
from utils.settings import settings

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Routers
app.include_router(devices.router, prefix="/api/devices")


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation errors (422) with the common response envelope."""
    msg = "Unprocessable input data, e.g., missing JSON field(s) or invalid path parameter(s)."
    body = ResponseGeneric(success=False, message=msg, details=exc.errors())
    return JSONResponse(jsonable_encoder(body), status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException) -> JSONResponse:
    return JSONResponse(exc.json, exc.status_code)


@app.get("/")
def root() -> ResponseGeneric:
    """Health check: the API is up and running."""
    return ResponseGeneric(message=f"{settings.APP_NAME} is running")
