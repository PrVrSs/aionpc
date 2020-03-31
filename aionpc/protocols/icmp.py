import asyncio
import socket
import struct
import time
import uuid
from ctypes import c_ubyte, c_ushort, c_char
from typing import final

from ..raw_connection import L2
from ..packet import Packet
from ..scheme import ProtocolScheme
from ..utils import resolve_address, struct_to_bytes
from .._packet_headers_tmp import IP, ICMP


ICMP_TYPES = {
    0: 'echo-reply',
    3: 'dest-unreach',
    4: 'source-quench',
    5: 'redirect',
    8: 'echo-request',
    9: 'router-advertisement',
    10: 'router-solicitation',
    11: 'time-exceeded',
    12: 'parameter-problem',
    13: 'timestamp-request',
    14: 'timestamp-reply',
    15: 'information-request',
    16: 'information-response',
    17: 'address-mask-request',
    18: 'address-mask-reply',
    30: 'traceroute',
    31: 'datagram-conversion-error',
    32: 'mobile-host-redirect',
    33: 'ipv6-where-are-you',
    34: 'ipv6-i-am-here',
    35: 'mobile-registration-request',
    36: 'mobile-registration-reply',
    37: 'domain-name-request',
    38: 'domain-name-reply',
    39: 'skip',
    40: 'photuris',
}


ICMP_CODES = {
    3: {
        0: 'network-unreachable',
        1: 'host-unreachable',
        2: 'protocol-unreachable',
        3: 'port-unreachable',
        4: 'fragmentation-needed',
        5: 'source-route-failed',
        6: 'network-unknown',
        7: 'host-unknown',
        9: 'network-prohibited',
        10: 'host-prohibited',
        11: 'TOS-network-unreachable',
        12: 'TOS-host-unreachable',
        13: 'communication-prohibited',
        14: 'host-precedence-violation',
        15: 'precedence-cutoff',
    },
    5: {
        0: 'network-redirect',
        1: 'host-redirect',
        2: 'TOS-network-redirect',
        3: 'TOS-host-redirect',
    },
    11: {
        0: 'ttl-zero-during-transit',
        1: 'ttl-zero-during-reassembly',
    },
    12: {
        0: 'ip-header-bad',
        1: 'required-option-missing',
    },
    40: {
        0: 'bad-spi',
        1: 'authentication-failed',
        2: 'decompression-failed',
        3: 'decryption-failed',
        4: 'need-authentification',
        5: 'need-authorization',
    },
}


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
    _id = None
    _header = None
    _payload = None

    @property
    def identifier(self):
        return self._id

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

        self._id = self._create_id()

        header = struct.pack('BbHHh', 8, 0, _checksum, self._id, seq)
        bytes_in_double = struct.calcsize('d')

        data = (192 - bytes_in_double) * 'A'
        data = struct.pack('d', time.time()) + data.encode('utf-8')

        _checksum = self.checksum(header + data)

        header = struct.pack('BbHHh', 8, 0, socket.htons(_checksum), self._id, seq)

        self._header = self.__scheme__.from_buffer_copy(header)
        self._payload = (c_char * len(data)).from_buffer_copy(data)

        return self


@final
class ICMPProtocol:

    __packet__ = ICMPPacket
    __connection__ = L2

    def __init__(self, options=()):
        self.options = options + ICMPProtocol.make_options()

    @classmethod
    async def echo_request(cls, host: str, count: int):
        host, port = await resolve_address(
            asyncio.get_running_loop(), socket.SOCK_RAW)(host)

        _connection = cls.__connection__(
            host=host,
            port=1,
            family=socket.AF_INET,
            proto=socket.IPPROTO_ICMP,
            package=cls.__packet__,
        )

        async with _connection as connection:
            for seq in range(1, count + 1):
                result = await connection.send(cls.__packet__().build(seq=seq))

                ip = IP.from_buffer(result)
                icmp = ICMP.from_buffer(result, ip.packet_length)

                print(f'from {ip.src} icmp_seq={icmp.seq} ttl={ip.ttl}')

    async def raw(self, packet: ICMPPacket):
        pass

    @staticmethod
    def make_options():
        return ()
