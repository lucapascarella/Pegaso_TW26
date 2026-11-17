DEVICE = {"serial": "SH-000123", "name": "Serra 3 - sonda nord", "device_class": "sensor", "site": "Sezze"}
CONFIG = {"version": 1, "min_temp": 12, "max_temp": 28, "sampling_sec": 30}


def test_without_token_is_401(client):
    assert client.get("/api/devices/list").status_code == 401


def test_invalid_token_is_401(client):
    resp = client.get("/api/devices/list", headers={"Authorization": "Bearer not-a-token"})
    assert resp.status_code == 401


def test_wrong_password_is_401(client, admin):
    resp = client.post("/api/auth/token", data={"username": "admin@test.example", "password": "wrong"})
    assert resp.status_code == 401


def test_viewer_can_read_but_not_change_config(client, admin, viewer):
    device_id = client.post("/api/devices", json=DEVICE, headers=admin).json()["data"]["id"]
    assert client.get(f"/api/devices/{device_id}/config", headers=viewer).status_code == 200
    assert client.put(f"/api/devices/{device_id}/config", json=CONFIG, headers=viewer).status_code == 403


def test_operator_cannot_create_devices(client, operator):
    assert client.post("/api/devices", json=DEVICE, headers=operator).status_code == 403


def test_me_never_returns_the_password_hash(client, viewer):
    data = client.get("/api/auth/me", headers=viewer).json()["data"]
    assert data["role"] == "viewer"
    assert "hashed_password" not in data
