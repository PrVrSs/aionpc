import abc
import asyncio
import socket
import uuid
import logging
from functools import partial
from typing import NamedTuple

from ._packet_headers_tmp import IP, ICMP


class Tt(NamedTuple):
    promise: int
    identifier: int


class IRawConnection(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    def _create_socket(family: int, proto: int): ...


class BaseRawConnection(IRawConnection):
    @staticmethod
    def _create_socket(family: int, proto: int):
        raise NotImplementedError

    @staticmethod
    def _create_id() -> int:
        return uuid.uuid4().int & 0xFFFF


# TODO: сделать реализацию Result<,>
class L2Protocol(asyncio.Protocol):
    def __init__(self, loop, pysocket, host, port, package):
        self._loop = loop
        self._socket = pysocket
        self._package_builder = package
        self._dst_address = host, port
        self._timeout = 2

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


class L2:
    def __init__(self, host: str, port: int, family: int, proto: int, package, loop=None):
        self._loop = loop or asyncio.get_running_loop()

        self._transport = None
        self._client = None

        self._pipe = self._create_pipe(family, proto)

        protocol_factory = partial(
            L2Protocol,
            loop=self._loop,
            pysocket=self._pipe,
            host=host,
            port=port,
            package=package
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
