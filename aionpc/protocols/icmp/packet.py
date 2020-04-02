import socket
import struct
import time
import uuid
from ctypes import c_ubyte, c_ushort, c_char
from typing import final

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
    def _checksum(buffer):
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

    def build(self, seq: int, proto: int, code: int):
        _checksum = 0

        _id = self._create_id()

        header = struct.pack('BbHHh', proto, code, _checksum, _id, seq)
        bytes_in_double = struct.calcsize('d')

        data = (192 - bytes_in_double) * 'A'
        data = struct.pack('d', time.time()) + data.encode('utf-8')

        _checksum = self._checksum(header + data)

        header = struct.pack(
            'BbHHh', proto, code, socket.htons(_checksum), _id, seq)

        self._header = self.__scheme__.from_buffer_copy(header)
        self._payload = (c_char * len(data)).from_buffer_copy(data)

        return self
