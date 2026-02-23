import asyncio
import logging
from typing import List

logger = logging.getLogger(__name__)


class EventBroadcaster:
    def __init__(self):
        self.clients: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self.clients.append(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue):
        if queue in self.clients:
            self.clients.remove(queue)

    async def broadcast(self, event_type: str, data: dict = None):
        """Broadcast event to all connected clients."""
        message = {"type": event_type, "data": data}
        for queue in self.clients:
            await queue.put(message)
        logger.info(
            f"SSE broadcast: {event_type} to {len(self.clients)} clients")


broadcaster = EventBroadcaster()
