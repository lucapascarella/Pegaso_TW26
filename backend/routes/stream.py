import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from modules.database import engine
from modules.dependencies import UserDep, get_stream_user
from modules.events import bus
from modules.security import STREAM_TOKEN_SEC, create_stream_token

router = APIRouter(tags=["Stream"])

KEEPALIVE_SEC = 15


@router.post("/token")
def get_stream_token(user: UserDep) -> dict:
    """
    Short-lived token (60 s) to open the SSE stream: EventSource cannot send the Authorization header
    """
    return {"stream_token": create_stream_token(user.id), "expires_in": STREAM_TOKEN_SEC}


@router.get("")
async def stream(request: Request, token: Annotated[str, Query()]) -> StreamingResponse:
    """
    Server-Sent Events: telemetry, status and config events for the dashboard
    """
    # The token is checked once, when the connection opens; then the stream stays open
    with Session(engine) as session:
        get_stream_user(session, token)

    queue = bus.subscribe()

    async def event_stream():
        try:
            yield "retry: 5000\n\n"  # the browser waits 5 s before reconnecting
            while not await request.is_disconnected():
                try:
                    event, data = await asyncio.wait_for(queue.get(), timeout=KEEPALIVE_SEC)
                    yield f"event: {event}\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keep-alive\n\n"  # a comment line keeps proxies from closing an idle connection
        finally:
            bus.unsubscribe(queue)

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
