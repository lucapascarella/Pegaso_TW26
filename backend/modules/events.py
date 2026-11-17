"""
Live events for the browser (Server-Sent Events).

The MQTT bridge runs in the paho thread, while the SSE connections live in the asyncio event loop of FastAPI.
publish() is thread-safe: it schedules the delivery inside the event loop with call_soon_threadsafe.
Every SSE connection has its own queue (fan-out: one event, many browsers).
"""
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self.loop: asyncio.AbstractEventLoop | None = None
        self.queues: set[asyncio.Queue] = set()

    def attach_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Called once in the lifespan, from the event loop."""
        self.loop = loop

    def subscribe(self) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        self.queues.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self.queues.discard(queue)

    def publish(self, event: str, data: dict) -> None:
        """Thread-safe: can be called from the MQTT thread or from an endpoint."""
        if self.loop is None or self.loop.is_closed():
            return
        self.loop.call_soon_threadsafe(self._fan_out, event, data)

    def _fan_out(self, event: str, data: dict) -> None:
        for queue in list(self.queues):
            try:
                queue.put_nowait((event, data))
            except asyncio.QueueFull:
                # A slow client must not block the others: its event is dropped
                logger.warning("SSE client too slow: event %s dropped", event)


# One bus for the whole application
bus = EventBus()
