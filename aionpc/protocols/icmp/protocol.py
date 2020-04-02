from typing import final

from .behavior import ICMPBehavior
from .packet import ICMPPacket
from .constants import ICMPTypes
from ..packet_headers_tmp import IP, ICMP
from ...layer import MediaLayer


@final
class ICMPProtocol:

    __packet__ = ICMPPacket
    __layer__ = MediaLayer
    __behavior__ = ICMPBehavior

    def __init__(self, options=()):
        self.options = options + ICMPProtocol.make_options()

    async def echo_request(self, host: str, count: int):
        _connection = await self.__layer__().create_connection(
            host=host,
            port=0,
            protocol_behavior=self.__behavior__(timeout=2)
        )

        async with _connection as connection:
            for seq in range(count):
                yield await connection.request(
                    self.__packet__().build(
                        seq=seq + 1,
                        proto=ICMPTypes.EchoRequest,
                        code=0,
                    )
                )

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
