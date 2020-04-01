import socket
import struct
import time
import uuid
from ctypes import c_ubyte, c_ushort, c_char
from typing import final

from ...layer import MediaLayer
from ...packet import Packet
from ...scheme import ProtocolScheme
from ...utils import struct_to_bytes
from ..._packet_headers_tmp import IP, ICMP


@final
class ICMPScheme(ProtocolScheme):
    type: c_ubyte
    code: c_ubyte
    checksum: c_ushort
    identifier: c_ushort
    seq: c_ushort


@final
class ICMPPacket(Packet):

    __scheme__ = ICMPScheme
    _header = None
    _payload = None

    @property
    def identifier(self):
        return self._header.identifier

    @property
    def header(self):
        return struct_to_bytes(self._header)

    @property
    def payload(self):
        return struct_to_bytes(self._payload)

    @property
    def data(self):
        return self.header + self.payload

    @staticmethod
    def _create_id() -> int:
        return uuid.uuid4().int & 0xFFFF

    @staticmethod
    def checksum(buffer):
        sum_ = 0
        count_to = (len(buffer) / 2) * 2
        count = 0

        while count < count_to:
            this_val = buffer[count + 1] * 256 + buffer[count]
            sum_ += this_val
            sum_ &= 0xffffffff
            count += 2

        if count_to < len(buffer):
            sum_ += buffer[len(buffer) - 1]
            sum_ &= 0xffffffff

        sum_ = (sum_ >> 16) + (sum_ & 0xffff)
        sum_ += sum_ >> 16
        answer = ~sum_
        answer &= 0xffff

        answer = answer >> 8 | (answer << 8 & 0xff00)

        return answer

    def build(self, seq: int):
        _checksum = 0

        _id = self._create_id()

        header = struct.pack('BbHHh', 8, 0, _checksum, _id, seq)
        bytes_in_double = struct.calcsize('d')

        data = (192 - bytes_in_double) * 'A'
        data = struct.pack('d', time.time()) + data.encode('utf-8')

        _checksum = self.checksum(header + data)

        header = struct.pack('BbHHh', 8, 0, socket.htons(_checksum), _id, seq)

        self._header = self.__scheme__.from_buffer_copy(header)
        self._payload = (c_char * len(data)).from_buffer_copy(data)

        return self


@final
class ICMPProtocol:

    __packet__ = ICMPPacket
    __layer__ = MediaLayer

    def __init__(self, options=()):
        self.options = options + ICMPProtocol.make_options()

    async def echo_request(self, host: str, count: int):
        _connection = await self.__layer__().create_connection(
            host=host, port=0, package_builder=self.__packet__)

        async with _connection as connection:
            for seq in range(count):
                yield await connection.send(self.__packet__().build(seq=seq + 1))

    async def raw(self, packet: ICMPPacket):
        pass

    @staticmethod
    def make_options():
        return ()


class EchoRequestPrinter:

    __line_tpl__ = (
        '{bytes} bytes from {host}: icmp_seq={seq} ttl={ttl} time={time} ms'
    ).format

    __stats_tpl__ = (
        '\n--- {host} ping statistics ---\n'
        '{count} packets transmitted, {rec} received, '
        '{lost}% packet loss, time 4001ms\n'
        'rtt min/avg/max/mdev = 54.745/56.539/58.894/1.601 ms'
    ).format

    def __init__(self, show=True):
        self.show = show
        self.packets = []

    def __call__(self, packet):
        self.packets.append(packet)

        if self.show:
            ip = IP.from_buffer(packet)
            icmp = ICMP.from_buffer(packet, ip.packet_length)

            print(
                self.__line_tpl__(
                    bytes=len(packet),
                    host=ip.src,
                    seq=icmp.seq,
                    ttl=ip.ttl,
                    time=45
                )
            )

    def stats(self):
        if self.show:
            print(
                self.__stats_tpl__(
                    host='123',
                    count=len(self.packets),
                    rec=len(self.packets),
                    lost=0,
                ))
