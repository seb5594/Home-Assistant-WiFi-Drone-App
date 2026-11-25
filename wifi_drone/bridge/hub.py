"""Share a single camera session among all clients."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import aclosing, suppress

from wifi_drone_connect import CameraAdapter, CameraError


class FrameHub:
    def __init__(self, camera: CameraAdapter | None) -> None:
        self.camera = camera
        self.state = "connecting" if camera else "unconfigured"
        self.latest: bytes | None = None
        self._changed = asyncio.Condition()
        self._generation = 0

    async def _update(self, frame: bytes | None, state: str) -> None:
        async with self._changed:
            self.latest = frame
            self.state = state
            self._generation += 1
            self._changed.notify_all()

    async def clear(self) -> None:
        await self._update(None, "reconnecting" if self.camera else "unconfigured")

    async def run(self) -> None:
        if self.camera is None:
            return
        while True:
            with suppress(CameraError):
                async with aclosing(self.camera.frames()) as frames:
                    async for frame in frames:
                        await self._update(frame, "streaming")
            await self.clear()
            await asyncio.sleep(2)

    async def frames(self) -> AsyncGenerator[bytes, None]:
        previous = -1
        while True:
            async with self._changed:
                await self._changed.wait_for(
                    lambda: self.latest is not None and self._generation != previous
                )
                previous = self._generation
                frame = self.latest
            assert frame is not None
            yield frame
