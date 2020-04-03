import asyncio

from aionpc.protocols import EchoRequestPrinter, ICMP


async def do_request(host):
    printer = EchoRequestPrinter(host=host)

    async for response in ICMP().echo_request(host=host, count=3):
        printer(response)

    return printer


async def main():
    tasks = [
        do_request(host='google.com'),
        do_request(host='twitch.tv'),
        do_request(host='ya.ru'),
    ]

    printers = await asyncio.gather(*tasks)

    for printer in printers:
        printer.stats()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
