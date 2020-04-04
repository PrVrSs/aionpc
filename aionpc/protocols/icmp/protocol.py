from typing import final

from .behavior import ICMPBehavior
from .constants import ICMPTypes
from .packet import ICMPPacket
from ...layer import MediaLayer


@final
class Protocol:

    __packet__ = ICMPPacket
    __layer__ = MediaLayer
    __behavior__ = ICMPBehavior

    async def echo_request(self, host: str, count: int):
        _connection = await self.__layer__().create_connection(
            protocol_behavior=self.__behavior__(timeout=2),
            host=host,
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
