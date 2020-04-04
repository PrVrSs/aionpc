from operator import itemgetter
from statistics import mean

from ..common import mdev
from ..packet_headers_tmp import IP, ICMP


class EchoRequestPrinter:

    __line_tpl__ = (
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
        self._packets = []

    def __call__(self, packet):
        _packet, _time = packet

        self._packets.append(packet)

        ip = IP.from_buffer(_packet)
        icmp = ICMP.from_buffer(_packet, ip.packet_length)

        print(
            self.__line_tpl__(
                bytes=len(_packet),
                host=ip.src,
                seq=icmp.seq,
                ttl=ip.ttl,
                time=_time
            )
        )

    def stats(self):
        print(
            self.__stats_tpl__(
                host=self._host,
                count=len(self._packets),
                rec=len(self._packets),
                lost=0,
                time=round(sum(_time for _, _time in self._packets)),  # TODO: include delay time
                min=min(self._packets, key=itemgetter(1))[1],
                max=max(self._packets, key=itemgetter(1))[1],
                avg=round(mean([_time for _, _time in self._packets]), 1),
                mdev=round(mdev([_time for _, _time in self._packets]), 3),
            )
        )
