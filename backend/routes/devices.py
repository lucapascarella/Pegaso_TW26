import uuid
from typing import Annotated

from fastapi import APIRouter, Query, status

from modules.crud import device as crud
from MQTT.bridge import bridge
from modules.events import bus
from modules.dependencies import AdminDep, EditorDep, SessionDep, UserDep
from modules.models.device import (DeviceClass, DeviceConfig, Reading, ReqConfigUpdate, ReqDeviceCreate, RespCount,
                                   RespDeviceConfig, RespDeviceDetails, RespDeviceList, RespReadingList)
from modules.models.models import ResponseGeneric

router = APIRouter(tags=["Device"])

# Reusable query parameters
QueryText = Annotated[str | None, Query(max_length=25)]
QuerySite = Annotated[str | None, Query(max_length=64)]


@router.get("/count")
def get_device_count(session: SessionDep, _: UserDep, device_class: DeviceClass | None = None,
                     site: QuerySite = None, query: QueryText = None) -> RespCount:
    """
    Count devices matching the filters (used by the frontend pagination)
    """
    return RespCount(data=crud.count_devices(session, device_class, site, query))


@router.get("/list")
def get_device_list(session: SessionDep, _: UserDep,
                    offset: Annotated[int, Query(ge=0, le=10000)] = 0,
                    limit: Annotated[int, Query(ge=1, le=100)] = 25,
                    device_class: DeviceClass | None = None,
                    site: QuerySite = None,
                    query: QueryText = None) -> RespDeviceList:
    """
    List devices with pagination and optional filters
    """
    devices = crud.list_devices(session, offset, limit, device_class, site, query)
    return RespDeviceList(message=f"Retrieved {len(devices)} device(s).", data=devices)


@router.get("/{device_id}")
def get_device_details(device_id: uuid.UUID, session: SessionDep, _: UserDep) -> RespDeviceDetails:
    """
    Get a single device by id
    """
    device = crud.get_device(session, device_id)
    config = crud.get_config(session, device_id)
    return RespDeviceDetails(message="Device details.", data=crud.to_short(device, config.version))


@router.post("", status_code=status.HTTP_201_CREATED)
def add_device(req: ReqDeviceCreate, session: SessionDep, _: AdminDep) -> RespDeviceDetails:
    """
    Register a new device with a default configuration (admin only)
    """
    device = crud.create_device(session, req)
    return RespDeviceDetails(message="Device created.", data=crud.to_short(device, 1))


@router.delete("/{device_id}")
def delete_device(device_id: uuid.UUID, session: SessionDep, _: AdminDep) -> ResponseGeneric:
    """
    Remove a device and its configuration (admin only)
    """
    crud.delete_device(session, device_id)
    return ResponseGeneric(message="Device deleted.")


@router.get("/{device_id}/config")
def get_device_config(device_id: uuid.UUID, session: SessionDep, _: UserDep) -> RespDeviceConfig:
    """
    Read the desired configuration (including its version)
    """
    config = crud.get_config(session, device_id)
    return RespDeviceConfig(data=DeviceConfig.model_validate(config, from_attributes=True))


@router.put("/{device_id}/config")
def put_device_config(device_id: uuid.UUID, req: ReqConfigUpdate, session: SessionDep, _: EditorDep) -> RespDeviceConfig:
    """
    Replace the desired configuration (admin, operator). Returns 409 if the version is not the current one.
    """
    config = crud.update_config(session, device_id, req)
    device = crud.get_device(session, device_id)
    # Retained + QoS 1: an offline device receives it when it reconnects
    bridge.publish_config(device.serial, config)
    bus.publish("config", {"device_id": str(device_id), "desired_version": config.version})
    return RespDeviceConfig(message=f"Configuration saved (version {config.version}).",
                            data=DeviceConfig.model_validate(config, from_attributes=True))


@router.get("/{device_id}/readings")
def get_device_readings(device_id: uuid.UUID, session: SessionDep, _: UserDep,
                        limit: Annotated[int, Query(ge=1, le=1000)] = 100) -> RespReadingList:
    """
    Latest telemetry samples, newest first
    """
    readings = crud.list_readings(session, device_id, limit)
    return RespReadingList(data=[Reading.model_validate(r, from_attributes=True) for r in readings])
