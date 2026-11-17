import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from modules.models.models import ResponseGeneric


class DeviceClass(str, Enum):
    Sensor = "sensor"      # publishes telemetry (temperature, humidity, ...)
    Actuator = "actuator"  # receives commands (fan, irrigation valve, ...)


class ReqDeviceCreate(BaseModel):
    """Request body to register a new device."""
    serial: str = Field(min_length=6, max_length=32, examples=["SH-000123"])
    name: str = Field(min_length=1, max_length=64, examples=["Serra 3 - sonda nord"])
    device_class: DeviceClass
    site: str = Field(max_length=64, examples=["Sezze"])


class DeviceShort(BaseModel):
    """Device as returned by the API."""
    id: uuid.UUID
    serial: str
    name: str
    device_class: DeviceClass
    site: str
    created_at: datetime


class RespDeviceList(ResponseGeneric):
    data: list[DeviceShort] = []


class RespDeviceDetails(ResponseGeneric):
    data: DeviceShort | None = None


def new_device(req: ReqDeviceCreate) -> DeviceShort:
    """Build a device from the request (id and timestamp are assigned by the server)."""
    return DeviceShort(id=uuid.uuid4(), created_at=datetime.now(timezone.utc), **req.model_dump())
