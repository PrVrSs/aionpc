# aionpc

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/PrVrSs/aionpc/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/)


# Examples

```python3
import asyncio

from aionpc import Client


async def do_request(host):
    icmp = Client.protocol_by_name(name='icmp')(config={'host': host})

    async for response in icmp.protocol.echo_request(count=3):
        icmp.printer(response)

    return icmp


async def main():
    tasks = [
        do_request(host='google.com'),
        do_request(host='twitch.tv'),
        do_request(host='ya.ru'),
    ]

    results = await asyncio.gather(*tasks)

    for proto in results:
        proto.printer.stats()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
```
