import asyncio
import collections
from asyncio import Future
from typing import Any, Coroutine

from pychanasync.errors import ChannelError, ChannelClosed, ChannelFull, ChannelEmpty

# # --- Context manager ---
# async def __aenter__(self):
#     return self
#
# async def __aexit__(self, exc_type, exc, tb):


class ProducerComponent:
    def __init__(self, producer: Future[Any], value: Any):
        self.producer = producer
        self.value = value


class Channel:
    """
    A channel instance provides a pipeline to stream data between  conccurent tasks scheduled
    in an event loop.

    :param bound:   In the case of a buffered channel this defines the boundary.
                    When value is None, which is the default value, the channel is unbuffered.

                    When Channel is unbuffered. receivers block unless there is a ready producer,
                    likewise consumers will block unless there is a ready receiver.

                    When Channel is buffered. Producers will only  block when the internal buffer is full and
                    receivers will only block when the buffer is empty.

    """

    def __init__(self, bound: int | None = None) -> None:

        # validate bound
        if bound is not None and bound < 0:
            raise ChannelError("Channel bound must be > 0")

        self._bound: int | None = bound
        if self._bound is not None:  # avoid buffer allocation entirely if not needed
            self.buffer: collections.deque[Any] = collections.deque(maxlen=bound)
        self._closed: bool = False
        # self.ready_receivers: deque[Future[Any]] = deque()
        self._ready_receivers: collections.deque[Future[Any]] = collections.deque()
        self._ready_producers: collections.deque[ProducerComponent] = (
            collections.deque()
        )

    def __repr__(self) -> str:
        return f"<Chan 0x{id(self):X}>"

    async def push(self, value: Any) -> Future[Any] | None:
        """
        pushes an item into the channel

        if channel is unbuffered, `push` will return immediately if a ready receiver is available.
        otherwise it will block and wait for one.

        if channel is buffered, `push` will put item in the channel and return immediately if there is space
        in buffer. otherwise it will  block and wait until there is space.

        :param value: the item to push into the channel

        """

        # check if channel is closed

        if self._closed:
            raise ChannelClosed(which_chan=self)

        if self._bound is None:
            # unbuffered
            if self._ready_receivers:
                ready_receiver: Future[Any] = self._ready_receivers.popleft()
                if not ready_receiver.cancelled():
                    ready_receiver.set_result(value)
                return

            else:
                ready_producer: Future[Any] = asyncio.Future()
                new_producer = ProducerComponent(ready_producer, value)
                self._ready_producers.append(new_producer)
                return await ready_producer

        # buffered
        # if buffered channel and there are pending receivers
        if self._ready_receivers:
            ready_receiver_buff: Future[Any] = self._ready_receivers.popleft()
            if not ready_receiver_buff.cancelled():
                ready_receiver_buff.set_result(value)
            return

        # if there is space
        if len(self.buffer) < self._bound:  # pyright: ignore[reportOperatorIssue]
            self.buffer.append(value)
            return

        # if there is no space in the buffer producer will wait
        ready_producer_buffered: Future[Any] = asyncio.Future()
        new_producer = ProducerComponent(ready_producer_buffered, value)
        self._ready_producers.append(new_producer)
        return await ready_producer_buffered

    def push_nowait(self, value: Any) -> Future[Any] | None:
        """
        Pushes an item into a buffered channel and does not wait or suspend  if the channel is full.

        `push_nowait` will put item in the channel and return immediately if there is space
        in buffer. otherwise it will   raise a `ChannelFull` exception.

        This operation is only allowed on  a buffered channel and will throw a `ChannelError` exception when
        used on a unbuffered channel.

        :param value: the item to push into the channel
        """

        # check if channel is closed

        if self._closed:
            raise ChannelClosed(which_chan=self)

        if self._bound is None:
            raise ChannelError(
                "push_nowait operation not allowed on unbuffered channels"
            )

        # buffered
        # if buffered channel and there are pending receivers
        if self._ready_receivers:
            ready_receiver_buff: Future[Any] = self._ready_receivers.popleft()
            if not ready_receiver_buff.cancelled():
                ready_receiver_buff.set_result(value)
            return

        # if there is space
        if len(self.buffer) < self._bound:  # pyright: ignore[reportOperatorIssue]
            self.buffer.append(value)
            return

        # if there is no space in the buffer producer will wait
        raise ChannelFull(which_chan=self)

    async def pull(self) -> None | Any:
        """
        Pulls an item from the channel

        If channel is unbuffered, `pull` will return with an immediately if a ready producer is available.
        Otherwise it will block and wait for one.

        If channel is buffered, `pull` will return an tem from the channel immediately if the buffer is not empty
        . Otherwise it will  block and wait until there is items in te channel.

        """
        if self._closed:
            raise ChannelClosed(which_chan=self)

        # unbuffered
        if self._bound is None:
            if self._ready_producers:
                producer_component: ProducerComponent = self._ready_producers.popleft()
                ready_producer: Future[Any] = producer_component.producer
                if not ready_producer.cancelled():
                    ready_producer.set_result(None)
                    return producer_component.value

            ready_receiver: Future[Any] = asyncio.Future()
            self._ready_receivers.append(ready_receiver)
            return await ready_receiver

        # buffered
        # if we have values in buffer
        if self.buffer:
            item = self.buffer.popleft()
            if self._ready_producers:
                producer_component_buff: ProducerComponent = (
                    self._ready_producers.popleft()
                )
                ready_producer_buff: Future[Any] = producer_component_buff.producer
                if not ready_producer_buff.cancelled():
                    ready_producer_buff.set_result(None)
                    self.buffer.append(producer_component_buff.value)
            return item

        # if buffered channel and buffer is empty then receiver will block
        ready_receiver_buff: Future[Any] = asyncio.Future()
        self._ready_receivers.append(ready_receiver_buff)
        return await ready_receiver_buff

    def pull_nowait(self) -> None | Any:
        """
        Pulls an item from the channel and does not wait or suspend when the channel is empty

        `pull_nowait` will return an tem from the channel immediately if the buffer is not empty
        . Otherwise it  will raise a `ChannelEmpty` exception.

        This operation is only allowed on a buffered channel and will throw a `ChannelError` exception when
        used on a unbuffered channel.

        """
        if self._closed:
            raise ChannelClosed(which_chan=self)

        if self._bound is None:
            raise ChannelError(
                "pull_nowait operation not allowed on unbuffered channels"
            )

        # buffered
        # if we have values in buffer
        if self.buffer:
            item = self.buffer.popleft()
            if self._ready_producers:
                producer_component_buff: ProducerComponent = (
                    self._ready_producers.popleft()
                )
                ready_producer_buff: Future[Any] = producer_component_buff.producer
                if not ready_producer_buff.cancelled():
                    ready_producer_buff.set_result(None)
                    self.buffer.append(producer_component_buff.value)
            return item

        # if buffered channel and buffer is empty then we shall raise an exception
        raise ChannelEmpty(which_chan=self)

    def close(self) -> None:
        """
        Closes the channel.

        All in flight producers are terminated with a `ChannelClosed` exception.

        In-flight receivers in a unbuffered channels are terminated as well but for a buffered channel, the buffer is
        drained , giving waiting receivers avaible items. All leftover receivers after that are terminated with are
        `ChannelClosed` exception.

        """

        # close channel
        self._closed = True

        # tell all waiting producers channel is closed
        for p in self._ready_producers:
            waiting_producer: Future[Any] = p.producer
            waiting_producer.set_exception(ChannelClosed(which_chan=self))

        waiting_recievers_to_satisfy: list[Any] = []
        # for buffered channels drain the buffer for all waiting receivers
        if self._bound:
            while self.buffer and self._ready_receivers:
                waiting_recievers_to_satisfy.append(
                    (self._ready_receivers.popleft(), self.buffer.popleft())
                )
            leftover_receivers = collections.deque(self._ready_receivers)
            self._ready_receivers.clear()

            # give waiting receivers items
            for receiver, item in waiting_recievers_to_satisfy:
                receiver.set_result(item)

            # give left over recievers exceptions
            for receiver in leftover_receivers:
                receiver.set_exception(ChannelClosed(which_chan=self))
            return

        # for unbuffered channels , no draining -- just give exceptions
        for r in self._ready_receivers:
            r.set_exception(ChannelClosed(which_chan=self))

    # async iteration
    def __aiter__(self):
        return self

    async def __anext__(self) -> Any:
        try:
            return await self.pull()
        except ChannelClosed:
            raise StopAsyncIteration

    # Context manager
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self.close()

    def empty(self) -> bool:
        """Returns True if the channel is empty, False otherwise."""
        return len(self.buffer) == 0
        # pass

    def full(self) -> bool:
        """Returns True if there are maxsize items in the channel."""
        return len(self.buffer) == self._bound

    def csize(self) -> int | None:
        """Return the number of items in the queue."""
        if self._bound:
            return len(self.buffer)
        return None

    @property
    def closed(self) -> bool:
        return self._closed


# -----------------------------------------------------------------
async def chanselect(
    *ops: tuple[Channel, Coroutine[None, None, Any]]
) -> tuple[Channel, Any | None]:
    """
    Provides a way to wait on multiple channel operations at once and returns the one that finishes first.
    Accepts the channel and its operatios as a tupe

    Example: Call select(
        (chan_a, chan_a.push(4)),
        (chan_b, chan_b.pull()),
        (chan_c, chan_c.push(40)),
    )

    If the operation is a `pull` it returns the channel and the value  ->  (chan,value).
    If the operation is a `push` it returns the channel and the None  ->  (chan,None).
    """

    # turn coroutines into tasks using helper wrapper
    tasks = [asyncio.create_task(_wrap(op[1], op[0])) for op in ops]

    done, pending = await asyncio.wait(
        tasks, return_when=asyncio.FIRST_COMPLETED
    )  # returns which ever task finishes first

    winner = done.pop()
    value, chan = await winner

    # cancel the rest
    for p in pending:
        p.cancel()

    return chan, value


async def _wrap(coro: Coroutine[None, None, Any], chan: Channel):
    val = await coro
    return val, chan
