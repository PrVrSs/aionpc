import socket
from typing import ClassVar, FrozenSet, Type

from .raw_connection import RawConnection
from .struct import Address
from .utils import resolve_host
from .protocol_behavior import ProtocolBehavior


class MediaLayer:

    __connection__: ClassVar[Type[RawConnection]] = RawConnection
    __protocols__: ClassVar[FrozenSet[str]] = frozenset((
        'ICMP',
    ))

    async def create_connection(
            self,
            protocol_behavior: ProtocolBehavior,
            host: str,
            port: int = 0
    ) -> RawConnection:
        dst_address = await resolve_host(
            socket_type=socket.SOCK_RAW,
        )(Address(host=host, port=port))

        return self.__connection__(
            address=dst_address,
            family=socket.AF_INET,
            proto=socket.IPPROTO_ICMP,
            protocol_behavior=protocol_behavior,
        )
