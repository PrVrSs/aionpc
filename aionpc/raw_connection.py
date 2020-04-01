import abc
import asyncio
import socket
import logging
from functools import partial

from .struct import Address
from ._packet_headers_tmp import IP, ICMP


class IRawConnection(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def _create_socket(family: int, proto: int): ...


class BaseRawConnection(IRawConnection):
    @staticmethod
    def _create_socket(family: int, proto: int):
        raise NotImplementedError


# TODO: сделать реализацию Result<,>
class RawProtocol(asyncio.Protocol):
    def __init__(
            self,
            loop: asyncio.AbstractEventLoop,
            pysocket: socket,
            address: Address,
            package_builder,
            timeout: int,
    ):
        self._loop = loop
        self._socket = pysocket
        self._package_builder = package_builder
        self._dst_address = address
        self._timeout = timeout

        self._promise = None
        self._transport = None
        self._identifier = None

    def connection_made(self, transport):
        self._transport = transport

    def data_received(self, data: bytes):
        ip = IP.from_buffer(data)
        icmp = ICMP.from_buffer(data, ip.packet_length)

        if self._identifier == icmp.id and icmp.type != 8:
            self._promise.set_result(data)

    def connection_lost(self, exc):
        if self._promise is not None:
            self._promise.cancel()

    def _send(self, package):
        self._promise = self._loop.create_future()
        self._identifier = package.identifier
        self._socket.sendto(package.data, self._dst_address)

        return asyncio.shield(self._promise)

    async def send(self, packet) -> bytes:
        try:
            try:
                return await asyncio.wait_for(
                    self._send(packet), self._timeout)
            except asyncio.TimeoutError:
                logging.debug('timed out')

        except asyncio.CancelledError:
            raise

        except Exception as e:
            logging.exception(e)

        return b''


class RawConnection:
    def __init__(
            self,
            address: Address,
            family: int,
            proto: int,
            package_builder,
            *,
            loop=None
    ):
        self._loop = loop or asyncio.get_running_loop()

        self._transport = None
        self._client = None

        self._pipe = self._create_pipe(family, proto)

        protocol_factory = partial(
            RawProtocol,
            loop=self._loop,
            pysocket=self._pipe,
            address=address,
            package_builder=package_builder,
            timeout=2,
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
