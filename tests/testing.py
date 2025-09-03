from context import Channel

import asyncio


async def hello(c: Channel, start: int, end: int):
    for i in range(start, end):
        # await asyncio.sleep(5)
        print("sending ", i)
        await c.push(i)
        print("sent ", i)


async def display(c: Channel):
    while True:

        print("started consuming")
        v = await c.pull()
        print("consumed", v)


async def main():

    c = Channel()

    asyncio.create_task(hello(c, 0, 100))
    asyncio.create_task(hello(c, 100, 200))
    # await asyncio.sleep(40)
    asyncio.create_task(display(c))
    asyncio.create_task(display(c))
    await asyncio.sleep(400)


if __name__ == "__main__":
    asyncio.run(main())
