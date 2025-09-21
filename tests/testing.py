from context import Channel

import asyncio

from pychanasync.errors import ChannelClosed


async def send(channel: Channel, start: int, end: int):
    async with channel as c:
        for i in range(start, end):
            await asyncio.sleep(2)
            print("sending ", i)
            await c.push(i)
            print("sent ", i)


async def display(c: Channel, n: str):
    while True:
        print(f"{n} started consuming")
        try:
            # await asyncio.sleep(5)
            v = await c.pull()
            print(f" {n} consumed", v)
        except ChannelClosed as e:
            print(f"channel {e.which_chan} closed for {n} ")
            break


async def main():

    c = Channel(bound=10)

    task1 = asyncio.create_task(send(c, 0, 12))
    # task1 = asyncio.create_task(send(c, 1, 2))

    # await asyncio.sleep(3)
    # async for item in c:
    #     print(f"got item {item=}")

    # task1 = asyncio.create_task(send(c, 3, 4))
    # task1 = asyncio.create_task(send(c, 5, 6))
    # task1 = asyncio.create_task(send(c, 7, 8))
    # # task2 = asyncio.create_task(send(c, 100, 200)
    # await asyncio.sleep(4)
    task3 = asyncio.create_task(display(c, "a"))
    task4 = asyncio.create_task(display(c, "b"))
    task5 = asyncio.create_task(display(c, "c"))
    task6 = asyncio.create_task(display(c, "d"))
    task7 = asyncio.create_task(display(c, "e"))
    # task4 = asyncio.create_task(display(c))

    await asyncio.gather(task1, task3, task4, task5, task6, task7)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
