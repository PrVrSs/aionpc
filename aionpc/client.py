from typing import Any, ClassVar, List, Optional

from more_itertools.recipes import first_true


class Protocols:

    clients: ClassVar[List['Protocols']] = []

    def __init_subclass__(cls, /, name: str, **kwargs: Any):
        super().__init_subclass__(**kwargs)
        cls.name = name
        cls.clients.append(cls)


class Client:

    @classmethod
    def protocol_by_name(cls, name: str) -> Optional[Any]:
        return first_true(
            Protocols.clients,
            default=None,
            pred=lambda protocol: protocol.name.lower() == name.lower(),
        )
