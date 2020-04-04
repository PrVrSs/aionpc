import asyncio
import ctypes
from ctypes import memmove, addressof, sizeof, create_string_buffer
from operator import itemgetter
from typing import Awaitable, Callable, Optional, Union

from more_itertools.recipes import first_true

from .struct import Address


_Structure = Union[ctypes.Array, ctypes.Structure]


def bytes_to_structure(struct: _Structure, byte: bytes) -> None:
    memmove(addressof(struct), byte, sizeof(struct))


def struct_to_bytes(struct: _Structure) -> bytes:
    buffer = create_string_buffer(sizeof(struct))
    memmove(buffer, addressof(struct), sizeof(struct))
    return buffer.raw


def int_to_bytes(number: int, size: int, *, notation: str = 'big') -> bytes:
    return number.to_bytes(size, notation)


def resolve_host(
        family: int = 0,
        socket_type: int = 0,
        proto: int = 0,
        flags: int = 0,
) -> Callable[[Address], Awaitable[Optional[Address]]]:
    sock_type_getter = itemgetter(1)
    dst_address_getter = itemgetter(4)

    async def inner(address: Address) -> Optional[Address]:
        info_all = await asyncio.get_running_loop().getaddrinfo(
            *address,
            family=family,
            proto=proto,
            flags=flags,
        )

        info = first_true(
            iterable=info_all,
            default=None,
            pred=lambda _: sock_type_getter(_) == socket_type,
        )

        return info and Address(*dst_address_getter(info))

    return inner
