import asyncio
from typing import Any
from .context import chanselect, Channel


async def consume_and_fill(chan: Channel, container: list[Any]):
    async for value in chan:
        container.append(value)


async def producer(chan: Channel, vals: list[Any]):
    for v in vals:
        await chan.push(v)

    await asyncio.sleep(0)  # yield contddrol one more time before a close
    chan.close()


async def produce_and_signal(chan: Channel, sigchan: Channel, vals: list[Any]):
    for v in vals:
        await chan.push(v)

    await sigchan.push(1)


async def wait_and_push(chan: Channel, wait_time: float, val: Any):
    await asyncio.sleep(wait_time)
    await chan.push(val)


async def wait_and_pull(chan: Channel, wait_time: float):
    await asyncio.sleep(wait_time)
    await chan.pull()


class TestChannel:
    async def test_simple_production_consumption_or_buffered_channel(self):

        chan = Channel(bound=1)
        vals: list[Any] = []

        consumer_task = asyncio.create_task(consume_and_fill(chan, vals))
        producer_task = asyncio.create_task(producer(chan, [45, 56, 78]))

        await asyncio.gather(consumer_task, producer_task)

        assert len(vals) == 3
        assert vals == [45, 56, 78]

    async def test_simple_production_consumption_for_unbuffered_channel(self):

        chan = Channel()
        vals: list[Any] = []

        async def uproducer(chan: Channel, vals: list[Any]):
            for v in vals:
                await chan.push(v)

            # await asyncio.sleep(0)  # we don't need to yield here - unbuffered channel comunication is sync.
            chan.close()

        consumer_task = asyncio.create_task(consume_and_fill(chan, vals))
        producer_task = asyncio.create_task(uproducer(chan, [45, 56, 78, 67, 89]))

        await asyncio.gather(consumer_task, producer_task)

        assert len(vals) == 5
        assert vals == [45, 56, 78, 67, 89]

    async def test_context_manager_protocol_closes_channel_when_done(self):
        chan = Channel(bound=5)

        async with chan as c:
            await c.push(5)
            await c.push(4)
            await c.push(3)

        assert chan.closed is True

    async def test_correct_channel_size_is_reported_for_buffered_channel(self):
        items = [f"item-{i}" for i in range(1000)]
        chan = Channel(bound=2000)

        async with chan as c:
            for i in items:
                await c.push(i)
            assert chan.csize() == len(items)

            await chan.push("another_item")

            assert chan.csize() == len(items) + 1

    async def test_channel_should_report_when_full_correctly_for_buffered_channel(self):
        items = [f"item-{i}" for i in range(1000)]
        chan = Channel(bound=2000)

        async with chan as c:
            for i in items:
                await c.push(i)
            assert chan.full() is False

            for i in items:
                await c.push(i)
            assert chan.full() is True

    async def test_channel_size_check_returns_none_for_unbuffered_channel(self):
        chan = Channel()
        assert chan.csize() is None

    async def test_chanselect_returns_the_correct_channel_whose_operation_finishes_first_for_unbuffered(
        self,
    ):
        chan_a = Channel()
        chan_b = Channel()
        chan_c = Channel()

        asyncio.create_task(wait_and_push(chan_a, 0.8, "item_a"))
        asyncio.create_task(wait_and_push(chan_b, 0.5, "item_b"))
        asyncio.create_task(wait_and_push(chan_c, 0.2, "item_c"))

        chan, value = await chanselect(
            (chan_a, chan_a.pull()), (chan_b, chan_b.pull()), (chan_c, chan_c.pull())
        )

        assert chan == chan_c
        assert value == "item_c"

    async def test_chanselect_returns_the_correct_channel_whose_operation_finishes_first_for_buffered(
        self,
    ):
        chan_a = Channel(bound=2)
        chan_b = Channel(bound=2)
        chan_c = Channel(bound=2)

        asyncio.create_task(wait_and_push(chan_a, 0.01, "item_a"))
        asyncio.create_task(wait_and_push(chan_b, 0.05, "item_b"))
        asyncio.create_task(wait_and_push(chan_c, 0.02, "item_c"))

        chan, value = await chanselect(
            (chan_a, chan_a.pull()), (chan_b, chan_b.pull()), (chan_c, chan_c.pull())
        )

        assert chan == chan_a
        assert value == "item_a"

    async def test_nothing_is_lost_when_multiple_producer_and_one_consumer_buffered(
        self,
    ):

        container: list[Any] = []
        chan = Channel(bound=5)
        chan_sig = Channel()

        async def listen_and_close(sigchan: Channel, chan_to_close: Channel):
            count = 0
            while True:
                if count == 5:
                    chan_to_close.close()  # close channel if all signals received
                    break
                await sigchan.pull()  # listen for signal
                count = count + 1

        producer_1 = asyncio.create_task(
            produce_and_signal(chan, chan_sig, [i for i in range(10)])
        )
        producer_2 = asyncio.create_task(
            produce_and_signal(chan, chan_sig, [i for i in range(10, 20)])
        )
        producer_3 = asyncio.create_task(
            produce_and_signal(chan, chan_sig, [i for i in range(20, 30)])
        )
        producer_4 = asyncio.create_task(
            produce_and_signal(chan, chan_sig, [i for i in range(30, 40)])
        )
        producer_5 = asyncio.create_task(
            produce_and_signal(chan, chan_sig, [i for i in range(40, 50)])
        )
        signal_listener = asyncio.create_task(listen_and_close(chan_sig, chan))
        consumer = asyncio.create_task(consume_and_fill(chan, container=container))

        await asyncio.gather(
            producer_1,
            producer_2,
            producer_3,
            producer_4,
            producer_5,
            signal_listener,
            consumer,
        )

        assert len(container) == 50
        assert container[len(container) - 1] == 49
