# Example from  Rob pike Talk - Google I/O 2012 - Go Concurrency Patterns
# https://youtu.be/f6kdp27TYZs
#
# DAISY CHAIN PATTERN
#


import asyncio
from typing import Any
from pychanasync.chan import Channel


async def f(left: Channel, right: Channel):
    val: Any = await right.pull()
    await left.push(val + 1)


async def main():
    chain_length = 10000

    lefmost_channel = Channel()

    left = lefmost_channel
    right = lefmost_channel

    for _ in range(chain_length):
        right = Channel()
        asyncio.create_task(f(left, right))
        left = right

    async def trigger(chan: Channel):
        await chan.push(1)

    asyncio.create_task(trigger(right))

    print(await lefmost_channel.pull())


if __name__ == "__main__":
    asyncio.run(main())
