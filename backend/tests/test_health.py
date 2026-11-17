def test_health_without_token(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "mqtt_connected" in body["data"]
