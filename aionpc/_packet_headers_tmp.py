import socket
import struct
from collections import namedtuple


IP_FIELDS = ['ver', 'ihl', 'ttl', 'proto', 'src', 'dst', 'packet_length']
ICMP_FIELDS = ['type', 'code', 'checksum', 'id', 'seq', 'payload']


class IP(namedtuple('IPHeader', IP_FIELDS)):

    @classmethod
    def from_buffer(cls, packet):
        ip_header = packet[:20]
        ip_header = struct.unpack('!BBHHHBBH4s4s', ip_header)

        tmp_ihl = ip_header[0]
        ip_version = tmp_ihl >> 4
        ip_ihl = tmp_ihl & 0xF

        packet_length = ip_ihl * 4

        ip_ttl = ip_header[5]
        ip_protocol = ip_header[6]
        ip_src = socket.inet_ntoa(ip_header[8])
        ip_dst = socket.inet_ntoa(ip_header[9])

        return cls(
            ip_version,
            ip_ihl,
            ip_ttl,
            ip_protocol,
            ip_src,
            ip_dst,
            packet_length,
        )


class ICMP(namedtuple('ICMPHeader', ICMP_FIELDS)):

    @classmethod
    def from_buffer(cls, packet, offset):
        icmp_header = packet[offset:offset + 8]
        icmp_header = struct.unpack('BbHHh', icmp_header)
        icmp_type = icmp_header[0]
        icmp_code = icmp_header[1]
        icmp_checksum = socket.htons(icmp_header[2])
        icmp_id = icmp_header[3]
        icmp_seq = icmp_header[4]
        icmp_payload = packet[offset + 8:]

        return cls(
            icmp_type,
            icmp_code,
            icmp_checksum,
            icmp_id,
            icmp_seq,
            icmp_payload,
        )
