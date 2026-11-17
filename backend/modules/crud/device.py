import uuid

from fastapi import status
from sqlmodel import Session, func, select

from modules.Exceptions import CustomException
from modules.models.device import (DeviceClass, DeviceConfigSql, DeviceShort, DeviceSql, ReadingSql, ReqConfigUpdate,
                                   ReqDeviceCreate, utc_now)


def _filtered(stmt, device_class: DeviceClass | None, site: str | None, query: str | None):
    """Apply the optional filters shared by list and count."""
    if device_class:
        stmt = stmt.where(DeviceSql.device_class == device_class)
    if site:
        stmt = stmt.where(DeviceSql.site == site)
    if query:
        stmt = stmt.where(DeviceSql.name.contains(query))
    return stmt


def count_devices(session: Session, device_class=None, site=None, query=None) -> int:
    stmt = _filtered(select(func.count()).select_from(DeviceSql), device_class, site, query)
    return session.exec(stmt).one()


def list_devices(session: Session, offset: int, limit: int, device_class=None, site=None, query=None) -> list[DeviceShort]:
    """Devices with the desired configuration version, to show which ones are out of sync."""
    stmt = select(DeviceSql, DeviceConfigSql.version).join(DeviceConfigSql, DeviceConfigSql.device_id == DeviceSql.id)
    stmt = _filtered(stmt, device_class, site, query)
    stmt = stmt.order_by(DeviceSql.site, DeviceSql.name).offset(offset).limit(limit)
    return [to_short(device, version) for device, version in session.exec(stmt).all()]


def to_short(device: DeviceSql, desired_version: int | None = None) -> DeviceShort:
    short = DeviceShort.model_validate(device, from_attributes=True)
    short.desired_version = desired_version
    return short


def get_device(session: Session, device_id: uuid.UUID) -> DeviceSql:
    device = session.get(DeviceSql, device_id)
    if device is None:
        raise CustomException(f"Device {device_id} not found.", None, status.HTTP_404_NOT_FOUND)
    return device


def get_device_by_serial(session: Session, serial: str) -> DeviceSql | None:
    return session.exec(select(DeviceSql).where(DeviceSql.serial == serial)).first()


def create_device(session: Session, req: ReqDeviceCreate) -> DeviceSql:
    stmt = select(DeviceSql).where(DeviceSql.serial == req.serial)
    exists = session.exec(stmt).first()
    if exists:
        raise CustomException(f"Serial {req.serial} already registered.", {"serial": req.serial}, status.HTTP_409_CONFLICT)

    device = DeviceSql(**req.model_dump())
    session.add(device)
    # Every device starts with a default desired configuration (version 1)
    session.add(DeviceConfigSql(device_id=device.id))
    session.commit()
    session.refresh(device)
    return device


def delete_device(session: Session, device_id: uuid.UUID) -> None:
    device = get_device(session, device_id)
    config = session.get(DeviceConfigSql, device_id)
    if config:
        session.delete(config)
    for reading in session.exec(select(ReadingSql).where(ReadingSql.device_id == device_id)).all():
        session.delete(reading)
    session.delete(device)
    session.commit()


def get_config(session: Session, device_id: uuid.UUID) -> DeviceConfigSql:
    get_device(session, device_id)  # 404 if the device does not exist
    return session.get(DeviceConfigSql, device_id)


def update_config(session: Session, device_id: uuid.UUID, req: ReqConfigUpdate) -> DeviceConfigSql:
    """
    Optimistic locking: the client sends the version it has read.
    If someone else saved in the meantime, the versions differ and the update is refused (409).
    """
    config = get_config(session, device_id)
    if req.version != config.version:
        raise CustomException("Configuration changed by another user: reload and retry.",
                              {"current_version": config.version}, status.HTTP_409_CONFLICT)

    config.min_temp = req.min_temp
    config.max_temp = req.max_temp
    config.sampling_sec = req.sampling_sec
    config.version += 1
    config.updated_at = utc_now()
    session.add(config)
    session.commit()
    session.refresh(config)
    return config


# ---------- Reported state (called by the MQTT bridge) ----------
def add_reading(session: Session, device: DeviceSql, payload: dict) -> ReadingSql:
    reading = ReadingSql(device_id=device.id, temperature=payload.get("temperature"), humidity=payload.get("humidity"))
    device.last_seen = reading.ts
    device.online = True
    session.add(reading)
    session.add(device)
    session.commit()
    return reading


def set_online(session: Session, device: DeviceSql, online: bool, config_version: int | None = None) -> None:
    device.online = online
    device.last_seen = utc_now()
    if config_version is not None:
        device.reported_version = config_version
    session.add(device)
    session.commit()


def set_reported_version(session: Session, device: DeviceSql, version: int) -> None:
    device.reported_version = max(device.reported_version, version)
    session.add(device)
    session.commit()


def list_readings(session: Session, device_id: uuid.UUID, limit: int) -> list[ReadingSql]:
    get_device(session, device_id)
    stmt = select(ReadingSql).where(ReadingSql.device_id == device_id).order_by(ReadingSql.ts.desc()).limit(limit)
    return list(session.exec(stmt).all())
