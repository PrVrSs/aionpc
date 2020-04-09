import asyncio
import time
from asyncio import AbstractEventLoop
from ctypes import sizeof
from typing import final, Optional

import attr

from ..headers import IPHeader, ICMPHeader
from ...protocol_behavior import ProtocolBehavior


@attr.s(frozen=True, slots=True)
class ICMPResponse:
    time = attr.ib()
    data = attr.ib()
    delay = attr.ib()


@final
class ICMPBehavior(ProtocolBehavior):
    def __init__(
            self,
            timeout: int,
            delay: int = 0.001,
            loop: Optional[AbstractEventLoop] = None,
    ):
        self._loop = loop or asyncio.get_running_loop()
        self._timeout = timeout
        self._delay = delay

        self._time = None
        self._promise = None
        self._identifier = None

    async def request(self, send, packet):
        if self._delay:
            await asyncio.sleep(self._delay)

        self._promise = self._loop.create_future()
        self._identifier = packet.identifier
        self._time = time.time()

        try:
            data, _time = await asyncio.wait_for(send(packet), self._timeout)
        except asyncio.TimeoutError:
            data, _time = b'', self._timeout * 1000

        return ICMPResponse(time=_time, data=data, delay=self._delay * 1000)

    def response(self, data: bytes) -> None:
        icmp_header = ICMPHeader.from_buffer_copy(data[sizeof(IPHeader):])

        if self._identifier == icmp_header.identifier and icmp_header.type != 8:
            _time = round((time.time() - self._time) * 1000, 1)
            self._promise.set_result((data, _time))

    def cancel(self):
        if self._promise is not None:
            self._promise.cancel()

    def complete_condition(self):
        return asyncio.shield(self._promise)
