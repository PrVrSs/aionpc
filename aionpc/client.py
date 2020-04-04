from typing import Optional, Type

from more_itertools.recipes import first_true

from .protocol import BaseProtocol


class Client:

    @classmethod
    def protocol_by_name(cls, name: str) -> Optional[Type[BaseProtocol]]:
        return first_true(
            BaseProtocol.protocols,
            default=None,
            pred=lambda protocol: protocol.name.lower() == name.lower(),
        )
