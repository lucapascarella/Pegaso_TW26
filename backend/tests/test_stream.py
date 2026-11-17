import asyncio

from modules.events import EventBus


def test_stream_token_cannot_open_the_api(client, viewer):
    stream_token = client.post("/api/stream/token", headers=viewer).json()["stream_token"]
    resp = client.get("/api/devices/list", headers={"Authorization": f"Bearer {stream_token}"})
    assert resp.status_code == 401


def test_api_token_cannot_open_the_stream(client, viewer):
    api_token = viewer["Authorization"].split()[1]
    assert client.get("/api/stream", params={"token": api_token}).status_code == 401


def test_event_bus_fan_out():
    async def scenario():
        bus = EventBus()
        bus.attach_loop(asyncio.get_running_loop())
        q1, q2 = bus.subscribe(), bus.subscribe()
        bus.publish("telemetry", {"temperature": 24.5})
        return await q1.get(), await q2.get()

    first, second = asyncio.run(scenario())
    assert first == second == ("telemetry", {"temperature": 24.5})
