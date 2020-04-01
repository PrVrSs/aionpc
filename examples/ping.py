import asyncio

from aionpc.protocols.icmp import ICMPProtocol


async def main():
    tasks = [
        ICMPProtocol.echo_request(host='google.com', count=3),
        ICMPProtocol.echo_request(host='twitch.tv', count=3),
        ICMPProtocol.echo_request(host='ya.ru', count=3),
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
