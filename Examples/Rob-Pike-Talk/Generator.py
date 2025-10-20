# Example from  Rob pike Talk - Google I/O 2012 - Go Concurrency Patterns
# https://youtu.be/f6kdp27TYZs
#

# GENERATOR PATTERN

import asyncio
from random import randint
from typing import Any
from pychanasync.chan import Channel


async def boring() -> Channel:
    chan = Channel()  # We create a channel

    async def send_vals():  # Create a coroutine that sends value into the channel
        count = 0
        while True:
            await chan.push(f"boring {count}")  # blocking operation
            wait = randint(0, 3)
            await asyncio.sleep(wait)
            count += 1

    asyncio.create_task(
        send_vals()
    )  # Ceate a task which will lauch coroutine from inside the function

    return chan  # return the channel


async def main():

    chan = await boring()  # function that returns the channel

    for _ in range(5):
        val: Any = await chan.pull()
        print(val)

    print("your'e both boring. I'm leaving!")


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
