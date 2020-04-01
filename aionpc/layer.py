import socket

from .raw_connection import RawConnection
from .struct import Address
from .utils import resolve_host


class MediaLayer:

    __connection__ = RawConnection
    __protocols__ = frozenset((
        'ICMP',
    ))

    async def create_connection(self, host, port, package_builder):
        dst_address = await resolve_host(
            socket_type=socket.SOCK_RAW,
        )(Address(host=host, port=port))

        return self.__connection__(
            address=dst_address,
            family=socket.AF_INET,
            proto=socket.IPPROTO_ICMP,
            package_builder=package_builder,
        )
