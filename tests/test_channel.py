import asyncio
from typing import Any
from context import chanselect, Channel


class TestChannel:
    async def test_simple_production_consumption_or_buffered_channel(self):

        chan = Channel(bound=1)
        vals: list[Any] = []

        async def consume_and_fill(chan: Channel, container: list[Any]):
            async for value in chan:
                container.append(value)

        async def producer(chan: Channel, vals: list[Any]):
            for v in vals:
                await chan.push(v)

            await asyncio.sleep(0)  # yield contddrol one more time before a close
            chan.close()

        consumer_task = asyncio.create_task(consume_and_fill(chan, vals))
        producer_task = asyncio.create_task(producer(chan, [45, 56, 78]))

        await asyncio.gather(consumer_task, producer_task)

        assert len(vals) == 3
        assert vals == [45, 56, 78]

    async def test_simple_production_consumption_for_unbuffered_channel(self):

        chan = Channel()
        vals: list[Any] = []

        async def consume_and_fill(chan: Channel, container: list[Any]):
            async for value in chan:
                container.append(value)

        async def producer(chan: Channel, vals: list[Any]):
            for v in vals:
                await chan.push(v)

            # await asyncio.sleep(0)  # we don't need to yield here - unbuffered channel comunication is sync.
            chan.close()

        consumer_task = asyncio.create_task(consume_and_fill(chan, vals))
        producer_task = asyncio.create_task(producer(chan, [45, 56, 78, 67, 89]))

        await asyncio.gather(consumer_task, producer_task)

        assert len(vals) == 5
        assert vals == [45, 56, 78, 67, 89]
