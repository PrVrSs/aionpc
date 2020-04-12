import asyncio
from functools import wraps
from itertools import count as counter

import click

from aionpc import l3_transport, ip_header, packet_factory, ICMPv4Format


def async_click(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import uvloop
        uvloop.install()
        return asyncio.run(func(*args, **kwargs), debug=True)

    return wrapper


def echo_request_tpl():
    return packet_factory(
        fields=(
            ('type', 8),
            ('code', 0),
            'checksum',
            'identifier',
            'sequence',
            'payload',
        ),
        scheme=ICMPv4Format,
    )


class Ping:
    def __init__(self, count, dst):
        self._max = count
        self._counter = counter()
        self._ip_header = ip_header(dst=dst)
        self._icmp = echo_request_tpl()
        self._transport = l3_transport()

    async def _fetch_data(self):
        if (seq := next(self._counter)) < self._max:
            return await self._transport.send(self._ip_header + self._icmp(seq))

    def __await__(self):
        return self.__await_impl__().__await__()

    async def __await_impl__(self):
        return [response async for response in self]

    def __aiter__(self):
        return self

    async def __anext__(self):
        if response := await self._fetch_data():
            return response

        raise StopAsyncIteration


@click.command()
@click.option('--count', '-c', default=5, type=int)
@click.option('--destination', '-dst', default='127.0.0.1', type=str)
@async_click
async def main(count, destination):
    async for response in Ping(count=count, dst=destination):
        print(response)


if __name__ == '__main__':
    main()
