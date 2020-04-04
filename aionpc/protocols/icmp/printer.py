from operator import attrgetter
from statistics import mean

from ..common import mdev
from ..packet_headers_tmp import IP, ICMP


class EchoRequestPrinter:

    __received_tpl__ = (
        '{bytes} bytes from {host}: icmp_seq={seq} ttl={ttl} time={time} ms'
    ).format

    __stats_tpl__ = (
        '\n--- {host} ping statistics ---\n'
        '{count} packets transmitted, {rec} received, '
        '{lost}% packet loss, time {time}ms\n'
        'rtt min/avg/max/mdev = {min}/{avg}/{max}/{mdev} ms'
    ).format

    def __init__(self, host: str):
        self._host = host
        self._loss_packets = set()
        self._received_packets = set()

    def __call__(self, packet):
        if not packet.data:
            self._loss_packets.add(packet)
            return

        self._received_packets.add(packet)

        ip = IP.from_buffer(packet.data)
        icmp = ICMP.from_buffer(packet.data, ip.packet_length)

        print(self._received_msg(ip, icmp, packet.time, len(packet.data)))

    def stats(self):
        print(self._stats_msg())

    def _received_msg(self, ip, icmp, _time, usize):
        return self.__received_tpl__(
                bytes=usize,
                host=ip.src,
                seq=icmp.seq,
                ttl=ip.ttl,
                time=_time,
            )

    def _stats_msg(self):
        return self.__stats_tpl__(
            host=self._host,
            count=len(self._loss_packets) + len(self._received_packets),
            rec=len(self._received_packets),
            lost=self._calc_loss(),
            time=round(sum(packet.time for packet in self._received_packets)),
            min=min(self._received_packets, key=attrgetter('time')).time,
            max=max(self._received_packets, key=attrgetter('time')).time,
            avg=round(
                mean([packet.time for packet in self._received_packets]), 1),
            mdev=round(
                mdev([packet.time for packet in self._received_packets]), 3),
        )

    def _calc_loss(self):
        return round(
            len(self._loss_packets) * 100
            /
            (len(self._loss_packets) + len(self._received_packets))
        )
