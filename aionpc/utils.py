import asyncio
from ctypes import memmove, addressof, sizeof, create_string_buffer
from operator import itemgetter
from typing import Awaitable, Callable, Optional

from more_itertools.recipes import first_true

from .struct import Address


def bytes_to_structure(st, byte):
    memmove(addressof(st), byte, sizeof(st))


def struct_to_bytes(st):
    buffer = create_string_buffer(sizeof(st))
    memmove(buffer, addressof(st), sizeof(st))
    return buffer.raw


def int_to_bytes(number, size, *, notation='big'):
    return number.to_bytes(size, notation)


def resolve_address(
        family: int = 0,
        socket_type: int = 0,
        proto: int = 0,
        flags: int = 0
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
