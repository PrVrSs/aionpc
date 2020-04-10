import struct
from ctypes import sizeof
from ipaddress import ip_address
from operator import attrgetter
from statistics import mean

from ..common import mdev
from ..headers import IPHeader, ICMPHeader


class EchoRequestPrinter:

    __received_tpl__ = (
        '{bytes} bytes from {host}: icmp_seq={seq} ttl={ttl} time={time} ms'
    ).format

    __stats_header_tpl__ = '\n--- {host} ping statistics ---\n'.format

    __stats_body_tpl__ = (
        '{count} packets transmitted, {rec} received, '
        '{lost}% packet loss, time {time}ms\n'
    ).format

    __stats_footer_tpl__ = (
        'rtt min/avg/max/mdev = {min}/{avg}/{max}/{mdev} ms').format

    def __init__(self, host: str):
        self._host = host
        self._loss_packets = set()
        self._received_packets = set()

    def __call__(self, packet):
        if not packet.data:
            self._loss_packets.add(packet)
            return

        self._received_packets.add(packet)

        ip_header = IPHeader.from_buffer_copy(packet.data)
        icmp_header = ICMPHeader.from_buffer_copy(packet.data[sizeof(IPHeader):])

        print(self._received_msg(
            ip_header,
            icmp_header,
            packet.time,
            len(packet.data),
        ))

    def stats(self):
        msg = self._stats_header_msg() + self._stats_body_msg()

        if self._received_packets:
            msg += self._stats_footer_msg()

        print(msg)

    def _received_msg(self, ip, icmp, _time, usize) -> str:
        return self.__received_tpl__(
                bytes=usize,
                host=ip_address(struct.pack('<L', ip.src)),
                seq=icmp.seq,
                ttl=ip.ttl,
                time=_time,
            )

    def _stats_header_msg(self) -> str:
        return self.__stats_header_tpl__(host=self._host)

    def _stats_body_msg(self) -> str:
        return self.__stats_body_tpl__(
            count=len(self._loss_packets) + len(self._received_packets),
            rec=len(self._received_packets),
            lost=self._calc_loss(),
            time=self._calc_sum_time(),
        )

    def _stats_footer_msg(self) -> str:
        return self.__stats_footer_tpl__(
            min=min(self._received_packets, key=attrgetter('time')).time,
            max=max(self._received_packets, key=attrgetter('time')).time,
            avg=round(
                mean([packet.time for packet in self._received_packets]), 1),
            mdev=round(
                mdev([packet.time for packet in self._received_packets]), 3),
        )

    def _calc_sum_time(self):
        return round(
            sum(
                packet.time + packet.delay
                for packet in self._received_packets | self._loss_packets
            )
        )

    def _calc_loss(self):
        return round(
            len(self._loss_packets) * 100
            /
            (len(self._loss_packets) + len(self._received_packets))
        )
