import json

from MQTT.bridge import MqttBridge
from modules.crud import device as crud
from modules.models.device import ReqConfigUpdate, ReqDeviceCreate

DEVICE = ReqDeviceCreate(serial="SH-000123", name="Serra 3 - sonda nord", device_class="sensor", site="Sezze")


class FakeBridge(MqttBridge):
    """Records the published configurations instead of sending them to a broker."""
    def __init__(self):
        super().__init__()
        self.sent = []

    def publish_config(self, serial, config):
        self.sent.append((serial, config.version))


def test_telemetry_is_stored(session):
    device = crud.create_device(session, DEVICE)
    bridge = FakeBridge()
    bridge.handle(session, "sensorhub/SH-000123/telemetry", json.dumps({"temperature": 24.5, "humidity": 60}).encode())
    readings = crud.list_readings(session, device.id, 10)
    assert len(readings) == 1 and readings[0].temperature == 24.5


def test_offline_device_gets_latest_config_when_back_online(session):
    device = crud.create_device(session, DEVICE)
    bridge = FakeBridge()
    # The device goes offline (LWT published by the broker)
    bridge.handle(session, "sensorhub/SH-000123/status", b'{"online": false}')
    # Meanwhile the agronomist saves version 2
    crud.update_config(session, device.id, ReqConfigUpdate(version=1, min_temp=12, max_temp=28, sampling_sec=10))
    # The device comes back online still running version 1
    bridge.handle(session, "sensorhub/SH-000123/status", b'{"online": true, "config_version": 1}')
    assert bridge.sent == [("SH-000123", 2)]


def test_device_in_sync_receives_nothing(session):
    crud.create_device(session, DEVICE)
    bridge = FakeBridge()
    bridge.handle(session, "sensorhub/SH-000123/status", b'{"online": true, "config_version": 1}')
    assert bridge.sent == []


def test_unknown_device_is_ignored(session):
    bridge = FakeBridge()
    bridge.handle(session, "sensorhub/XX-999999/telemetry", b'{"temperature": 99}')
    assert bridge.sent == []
