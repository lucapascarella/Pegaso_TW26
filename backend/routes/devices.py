import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from modules.Exceptions import CustomException
from modules.models.device import DeviceClass, DeviceShort, ReqDeviceCreate, RespDeviceDetails, RespDeviceList, new_device

router = APIRouter(tags=["Device"])

# In-memory storage: it is replaced by SQLite + SQLModel in TW2
fake_db: dict[uuid.UUID, DeviceShort] = {}


@router.get("/list")
def get_device_list(offset: Annotated[int, Query(ge=0, le=10000)] = 0,
                    limit: Annotated[int, Query(ge=1, le=100)] = 25,
                    device_class: DeviceClass | None = None,
                    query: Annotated[str | None, Query(max_length=25)] = None) -> RespDeviceList:
    """
    List devices with pagination and optional filters
    """
    devices = list(fake_db.values())
    if device_class:
        devices = [d for d in devices if d.device_class == device_class]
    if query:
        devices = [d for d in devices if query.lower() in d.name.lower()]

    page = devices[offset:offset + limit]
    return RespDeviceList(message=f"Retrieved {len(page)} device(s).", data=page)


@router.get("/{device_id}")
def get_device_details(device_id: uuid.UUID) -> RespDeviceDetails:
    """
    Get a single device by id
    """
    device = fake_db.get(device_id)
    if device is None:
        raise CustomException(f"Device {device_id} not found.", None, status.HTTP_404_NOT_FOUND)

    return RespDeviceDetails(message="Device details.", data=device)


@router.post("", status_code=status.HTTP_201_CREATED)
def add_device(req: ReqDeviceCreate) -> RespDeviceDetails:
    """
    Register a new device
    """
    if any(d.serial == req.serial for d in fake_db.values()):
        raise CustomException(f"Serial {req.serial} already registered.", {"serial": req.serial}, status.HTTP_409_CONFLICT)

    device = new_device(req)
    fake_db[device.id] = device
    return RespDeviceDetails(message="Device created.", data=device)
