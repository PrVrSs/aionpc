from ctypes import *
from operator import itemgetter
from typing import Optional, Tuple

from more_itertools.recipes import first_true


def bytes_to_structure(st, byte):
    memmove(addressof(st), byte, sizeof(st))


def struct_to_bytes(st):
    buffer = create_string_buffer(sizeof(st))
    memmove(buffer, addressof(st), sizeof(st))
    return buffer.raw


def int_to_bytes(number, size, notation='big'):
    return number.to_bytes(size, notation)


def resolve_address(loop, sock_type):
    sock_type_getter = itemgetter(1)
    dst_address_getter = itemgetter(4)

    async def inner(host: str, port: int = 1) -> Optional[Tuple[str, int]]:
        info = first_true(
            iterable=await loop.getaddrinfo(host=host, port=port),
            default=None,
            pred=lambda _: sock_type_getter(_) == sock_type,
        )

        return info and dst_address_getter(info)

    return inner
