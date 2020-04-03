import socket
import struct
import time
import uuid
from ctypes import c_ubyte, c_ushort, c_char
from typing import final

from ..utils import checksum
from ...packet import Packet
from ...scheme import ProtocolScheme
from ...utils import struct_to_bytes


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
    def _generate_payload(size: int = 28):
        return struct.pack('d', time.time()) + ('A' * size).encode('utf-8')

    def build(self, seq: int, proto: int, code: int, size: int = 0):
        _checksum = 0
        _id = self._create_id()

        header = struct.pack('BbHHh', proto, code, _checksum, _id, seq)

        _payload = self._generate_payload()
        _checksum = checksum(header + _payload)

        header = struct.pack(
            'BbHHh', proto, code, socket.htons(_checksum), _id, seq)

        self._header = self.__scheme__.from_buffer_copy(header)
        self._payload = (c_char * len(_payload)).from_buffer_copy(_payload)

        return self
