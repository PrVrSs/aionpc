import asyncio
import time
from typing import final

from ..packet_headers_tmp import IP, ICMP
from ...protocol_behavior import ProtocolBehavior


@final
class ICMPBehavior(ProtocolBehavior):
    def __init__(self, timeout, loop=None):
        self._loop = loop or asyncio.get_running_loop()
        self._timeout = timeout

        self._time = None
        self._promise = None
        self._identifier = None

    async def request(self, send, packet):
        self._promise = self._loop.create_future()
        self._identifier = packet.identifier
        self._time = time.time()

        try:
            response = await asyncio.wait_for(send(packet), self._timeout)
        except asyncio.TimeoutError:
            response = b''

        return response

    def response(self, data: bytes) -> None:
        ip = IP.from_buffer(data)
        icmp = ICMP.from_buffer(data, ip.packet_length)

        if self._identifier == icmp.id and icmp.type != 8:
            _time = round((time.time() - self._time) * 1000, 1)
            self._promise.set_result((data, _time))

    def cancel(self):
        if self._promise is not None:
            self._promise.cancel()

    def complete_condition(self):
        return asyncio.shield(self._promise)
