from typing import Any, ClassVar, List, Type


class BaseProtocol:

    protocols: ClassVar[List[Type['BaseProtocol']]] = []
    name: str

    def __init_subclass__(cls, /, name: str, **kwargs: Any):
        super().__init_subclass__(**kwargs)  # type: ignore
        cls.name = name
        cls.protocols.append(cls)
