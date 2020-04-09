from ctypes import *


class IPHeader(Structure):
    _fields_ = [
        ('version', c_uint8, 4),
        ('ihl', c_uint8, 4),
        ('tos', c_uint8),
        ('len', c_uint16),
        ('id', c_uint16),
        ('offset', c_uint16),
        ('ttl', c_uint8),
        ('protocol_num', c_uint8),
        ('sum', c_uint16),
        ('src', c_uint32),
        ('dst', c_uint32),
    ]


class ICMPHeader(Structure):
    _fields_ = [
        ('type', c_ubyte),
        ('code',  c_ubyte),
        ('checksum', c_ushort),
        ('identifier', c_ushort),
        ('seq', c_ushort),
    ]


protocol_map = {
    1: ICMPHeader,
}
