# Example from  Rob pike Talk - Google I/O 2012 - Go Concurrency Patterns
# https://youtu.be/f6kdp27TYZs

# FAN IN PATTERN - WITH CHANSELECT


import asyncio
from random import randint
from typing import Any

from pychanasync.chan import Channel, chanselect


async def boring(msg) -> Channel:
    chan = Channel()  # We create a channel

    async def send_vals():  # Create a coroutine that sends value into the channel
        count = 0
        while True:
            await chan.push(f"{msg} {count}")  # blocking operation
            wait = randint(0, 3)
            await asyncio.sleep(wait)
            count += 1

    asyncio.create_task(
        send_vals()
    )  # Ceate a task which will lauch coroutine from inside the function

    return chan  # return the channel


async def fanin(input_1: Channel, input_2: Channel) -> Channel:
    chan = Channel()

    async def push_into():  # the fan in function is taking values from  the 2 channels and fanning
        # it on to one channel
        while True:
            _, value = await chanselect(
                (input_1, input_1.pull()), (input_2, input_2.pull())
            )
            await chan.push(value)

    asyncio.create_task(push_into())

    return chan


async def main():
    chan = await fanin(await boring("Joe"), await boring("Ann"))
    for _ in range(10):
        val: Any = await chan.pull()
        print(val)
    print("your'e both boring. I'm leaving!")


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
