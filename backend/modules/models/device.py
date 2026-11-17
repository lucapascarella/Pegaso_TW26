import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field as PydField, model_validator
from sqlmodel import Field, SQLModel

from modules.models.models import ResponseGeneric


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DeviceClass(str, Enum):
    Sensor = "sensor"      # publishes telemetry (temperature, humidity, ...)
    Actuator = "actuator"  # receives commands (fan, irrigation valve, ...)


# ---------- Tables ----------
class DeviceSql(SQLModel, table=True):
    __tablename__ = "device"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    serial: str = Field(index=True, unique=True, max_length=32)
    name: str = Field(max_length=64)
    device_class: DeviceClass
    site: str = Field(max_length=64, index=True)
    created_at: datetime = Field(default_factory=utc_now)


class DeviceConfigSql(SQLModel, table=True):
    """Desired configuration of a device. 'version' grows at every change (optimistic locking)."""
    __tablename__ = "device_config"

    device_id: uuid.UUID = Field(foreign_key="device.id", primary_key=True)
    version: int = 1
    min_temp: float = 10.0
    max_temp: float = 30.0
    sampling_sec: int = 60
    updated_at: datetime = Field(default_factory=utc_now)


# ---------- Requests ----------
class ReqDeviceCreate(BaseModel):
    """Request body to register a new device."""
    serial: str = PydField(min_length=6, max_length=32, examples=["SH-000123"])
    name: str = PydField(min_length=1, max_length=64, examples=["Serra 3 - sonda nord"])
    device_class: DeviceClass
    site: str = PydField(max_length=64, examples=["Sezze"])


class ReqConfigUpdate(BaseModel):
    """New desired configuration. 'version' is the version the client has read."""
    version: int = PydField(ge=1)
    min_temp: float = PydField(ge=-20, le=60)
    max_temp: float = PydField(ge=-20, le=60)
    sampling_sec: int = PydField(ge=5, le=3600)

    @model_validator(mode="after")
    def check_range(self):
        if self.min_temp >= self.max_temp:
            raise ValueError("min_temp must be lower than max_temp")
        return self


# ---------- Responses ----------
class DeviceShort(BaseModel):
    id: uuid.UUID
    serial: str
    name: str
    device_class: DeviceClass
    site: str
    created_at: datetime


class DeviceConfig(BaseModel):
    version: int
    min_temp: float
    max_temp: float
    sampling_sec: int
    updated_at: datetime


class RespDeviceList(ResponseGeneric):
    data: list[DeviceShort] = []


class RespDeviceDetails(ResponseGeneric):
    data: DeviceShort | None = None


class RespDeviceConfig(ResponseGeneric):
    data: DeviceConfig | None = None


class RespCount(ResponseGeneric):
    data: int = 0
