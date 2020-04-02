import asyncio
import socket
from functools import partial

from .struct import Address
from .protocol_behavior import ProtocolBehavior


class RawProtocol(asyncio.Protocol):
    def __init__(
            self,
            pysocket: socket,
            address: Address,
            protocol_behavior: ProtocolBehavior,
    ):
        self._socket = pysocket
        self._dst_address = address
        self._protocol_behavior = protocol_behavior

        self._transport = None

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data: bytes):
        self._protocol_behavior.response(data)

    def connection_lost(self, exc):
        self._protocol_behavior.cancel()

    def _send(self, packet):
        self._socket.sendto(packet.data, self._dst_address)
        return self._protocol_behavior.complete_condition()

    async def request(self, packet):
        try:
            return await self._protocol_behavior.request(self._send, packet)
        except asyncio.CancelledError:
            raise
        except Exception:
            raise


class RawConnection:
    def __init__(
            self,
            address: Address,
            family: int,
            proto: int,
            protocol_behavior: ProtocolBehavior,
            *,
            loop=None
    ):
        self._loop = loop or asyncio.get_running_loop()

        self._transport = None
        self._client = None

        self._pipe = self._create_pipe(family, proto)

        protocol_factory = partial(
            RawProtocol,
            pysocket=self._pipe,
            address=address,
            protocol_behavior=protocol_behavior,
        )

        self._create_connection = partial(
            self._loop.connect_read_pipe,
            protocol_factory=protocol_factory,
            pipe=self._pipe,
        )

    @staticmethod
    def _create_pipe(family: int, proto: int) -> socket:
        return socket.socket(
            family=family,
            type=socket.SOCK_RAW | socket.SOCK_NONBLOCK,
            proto=proto,
        )

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __aenter__(self):
        return await self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._transport.close()
        self._pipe.close()

    async def __await_impl__(self):
        self._transport, self._client = await self._create_connection()
        return self._client

    __iter__ = __await__
