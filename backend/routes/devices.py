import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from modules.crud import device as crud
from modules.dependencies import SessionDep
from modules.models.device import (DeviceClass, DeviceConfig, DeviceShort, ReqConfigUpdate, ReqDeviceCreate, RespCount,
                                   RespDeviceConfig, RespDeviceDetails, RespDeviceList)
from modules.models.models import ResponseGeneric

router = APIRouter(tags=["Device"])

# Reusable query parameters
QueryText = Annotated[str | None, Query(max_length=25)]
QuerySite = Annotated[str | None, Query(max_length=64)]


@router.get("/count")
def get_device_count(session: SessionDep, device_class: DeviceClass | None = None,
                     site: QuerySite = None, query: QueryText = None) -> RespCount:
    """
    Count devices matching the filters (used by the frontend pagination)
    """
    return RespCount(data=crud.count_devices(session, device_class, site, query))


@router.get("/list")
def get_device_list(session: SessionDep,
                    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
                    limit: Annotated[int, Query(ge=1, le=100)] = 25,
                    device_class: DeviceClass | None = None,
                    site: QuerySite = None,
                    query: QueryText = None) -> RespDeviceList:
    """
    List devices with pagination and optional filters
    """
    devices = crud.list_devices(session, offset, limit, device_class, site, query)
    return RespDeviceList(message=f"Retrieved {len(devices)} device(s).",
                          data=[DeviceShort.model_validate(d, from_attributes=True) for d in devices])


@router.get("/{device_id}")
def get_device_details(device_id: uuid.UUID, session: SessionDep) -> RespDeviceDetails:
    """
    Get a single device by id
    """
    device = crud.get_device(session, device_id)
    return RespDeviceDetails(message="Device details.", data=DeviceShort.model_validate(device, from_attributes=True))


@router.post("", status_code=status.HTTP_201_CREATED)
def add_device(req: ReqDeviceCreate, session: SessionDep) -> RespDeviceDetails:
    """
    Register a new device (with a default configuration)
    """
    device = crud.create_device(session, req)
    return RespDeviceDetails(message="Device created.", data=DeviceShort.model_validate(device, from_attributes=True))


@router.delete("/{device_id}")
def delete_device(device_id: uuid.UUID, session: SessionDep) -> ResponseGeneric:
    """
    Remove a device and its configuration
    """
    crud.delete_device(session, device_id)
    return ResponseGeneric(message="Device deleted.")


@router.get("/{device_id}/config")
def get_device_config(device_id: uuid.UUID, session: SessionDep) -> RespDeviceConfig:
    """
    Read the desired configuration (including its version)
    """
    config = crud.get_config(session, device_id)
    return RespDeviceConfig(data=DeviceConfig.model_validate(config, from_attributes=True))


@router.put("/{device_id}/config")
def put_device_config(device_id: uuid.UUID, req: ReqConfigUpdate, session: SessionDep) -> RespDeviceConfig:
    """
    Replace the desired configuration. Returns 409 if the version is not the current one.
    """
    config = crud.update_config(session, device_id, req)
    return RespDeviceConfig(message=f"Configuration saved (version {config.version}).",
                            data=DeviceConfig.model_validate(config, from_attributes=True))
