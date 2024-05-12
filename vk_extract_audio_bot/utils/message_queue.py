from asyncio import Lock, sleep
from collections.abc import (
    AsyncGenerator,
)

from pydantic import (
    NonNegativeInt,
    PositiveInt,
)


LISTEN_DELAY = 5.0


class MessageQueue:

    def __init__(self) -> None:
        self._queue: list[int] = []
        self._lock = Lock()

    async def put(self, message_id: int) -> None:
        async with self._lock:
            self._queue.append(message_id)

    async def get(self) -> int:
        async with self._lock:
            return self._queue.pop(0)

    async def pop(self) -> None:
        async with self._lock:
            self._queue.pop(0)

    async def top(self) -> int:
        async with self._lock:
            return self._queue[0]

    async def position(self, message_id: int) -> int:
        async with self._lock:
            return self._queue.index(message_id)

    async def listen_positions(
        self,
        message_id: PositiveInt,
        until: NonNegativeInt = 0,
    ) -> AsyncGenerator[int, None, None]:
        pos_old = -1
        while (pos := await self.position(message_id)) != until:
            if pos_old != pos:
                pos_old = pos
                yield pos
            await sleep(LISTEN_DELAY)
