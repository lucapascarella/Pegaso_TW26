DEVICE = {"serial": "SH-000123", "name": "Serra 3 - sonda nord", "device_class": "sensor", "site": "Sezze"}


def test_create_and_read_device(client):
    resp = client.post("/api/devices", json=DEVICE)
    assert resp.status_code == 201
    device_id = resp.json()["data"]["id"]

    resp = client.get(f"/api/devices/{device_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["serial"] == DEVICE["serial"]


def test_duplicate_serial_is_409(client):
    client.post("/api/devices", json=DEVICE)
    resp = client.post("/api/devices", json=DEVICE)
    assert resp.status_code == 409
    assert resp.json()["success"] is False


def test_invalid_body_is_422(client):
    resp = client.post("/api/devices", json={"serial": "123", "device_class": "toaster"})
    assert resp.status_code == 422


def test_config_optimistic_locking(client):
    device_id = client.post("/api/devices", json=DEVICE).json()["data"]["id"]
    config = client.get(f"/api/devices/{device_id}/config").json()["data"]
    assert config["version"] == 1

    new = {"version": 1, "min_temp": 12, "max_temp": 28, "sampling_sec": 30}
    first = client.put(f"/api/devices/{device_id}/config", json=new)
    assert first.status_code == 200
    assert first.json()["data"]["version"] == 2

    # A second user still holding version 1 must get a conflict
    second = client.put(f"/api/devices/{device_id}/config", json=new)
    assert second.status_code == 409
    assert second.json()["data"]["current_version"] == 2
