import asyncio
from asyncio.locks import Lock
import collections
from asyncio import Future
from ctypes import set_errno
from itertools import chain
import re
from typing import Any

from pychanasync.errors import ChanError, ChannelClosed


# # --- Context manager ---
# async def __aenter__(self):
#     return self
#
# async def __aexit__(self, exc_type, exc, tb):
#     self.close()
#
# # --- Async iteration ---
# def __aiter__(self):
#     return self
#
# async def __anext__(self):
#     try:
#         return await self.recv()
#     except ChannelClosed:
#         raise StopAsyncIteration


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
            raise ChanError("Channel bound must be > 0")

        self.bound: int | None = bound
        if self.bound is not None:  # avoid buffer allocation entirely if not needed
            self.buffer: collections.deque[Any] = collections.deque(maxlen=bound)
        self.closed: bool = False
        self.lock: Lock = asyncio.Lock()
        # self.ready_receivers: deque[Future[Any]] = deque()
        self.ready_receivers: collections.deque[Future[Any]] = collections.deque()
        self.ready_producers: collections.deque[ProducerComponent] = collections.deque()

    async def push(self, value: Any) -> Future[Any] | None:
        """
        Pushes an item into the channel

        If channel is unbuffered, `push` will return immediately if a ready receiver is available.
        Otherwise it will block and wait for one.

        :param value: The item to push into the channel

        """

        # check if channel is closed
        awaitable_future: Future[Any] | None = None

        async with self.lock:

            if self.closed:
                raise ChannelClosed

            if self.bound is None:
                # unbuffered
                if self.ready_receivers:
                    ready_receiver: Future[Any] = self.ready_receivers.popleft()
                    ready_receiver.set_result(value)
                    return

                else:
                    ready_producer: Future[Any] = asyncio.Future()
                    new_producer = ProducerComponent(ready_producer, value)
                    self.ready_producers.append(new_producer)
                    awaitable_future = ready_producer
                    # return await ready_producer
            else:
                # buffered
                # if buffered channel and there are pending receivers
                if self.ready_receivers:
                    ready_receiver_buff: Future[Any] = self.ready_receivers.popleft()
                    ready_receiver_buff.set_result(value)
                    return

                # if there is space
                if (
                    len(self.buffer) < self.bound
                ):  # pyright: ignore[reportOperatorIssue]
                    self.buffer.append(value)
                    return

                # if there is no space in the buffer producer will wait
                ready_producer_buffered: Future[Any] = asyncio.Future()
                new_producer = ProducerComponent(ready_producer_buffered, value)
                self.ready_producers.append(new_producer)
                awaitable_future = ready_producer_buffered
                # return await ready_producer_buffered
                #
            return await awaitable_future

    async def pull(self) -> None | Any:

        if self.closed:
            raise ChannelClosed

        # unbuffered
        if self.bound is None:
            if self.ready_producers:
                producer_component: ProducerComponent = self.ready_producers.popleft()
                ready_producer: Future[Any] = producer_component.producer
                ready_producer.set_result(None)
                return producer_component.value

            ready_receiver: Future[Any] = asyncio.Future()
            self.ready_receivers.append(ready_receiver)
            return await ready_receiver

        # buffered
        # if we have values in buffer
        if self.buffer:
            item = self.buffer.popleft()
            if self.ready_producers:
                producer_component_buff: ProducerComponent = (
                    self.ready_producers.popleft()
                )
                ready_producer_buff: Future[Any] = producer_component_buff.producer
                ready_producer_buff.set_result(None)
                self.buffer.append(producer_component_buff.value)
            return item

        # if buffered channel and buffer is empty then receiver will block
        ready_receiver_buff: Future[Any] = asyncio.Future()
        self.ready_receivers.append(ready_receiver_buff)
        return await ready_receiver_buff

    def close(self) -> None:

        self.closed = True
        # tell all waiting producers
        for p in self.ready_producers:
            waiting_producer: Future[Any] = p.producer
            waiting_producer.set_exception(ChannelClosed)

        # tell all waiting receivers
        for r in self.ready_receivers:
            r.set_exception(ChannelClosed)
