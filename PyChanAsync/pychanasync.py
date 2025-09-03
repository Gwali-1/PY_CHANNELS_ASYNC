import asyncio
import collections
from asyncio import Future
from ctypes import set_errno
from typing import Any

from PyChanAsync.errors import ChanError


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
        self.closed: bool = False
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

        if self.bound is None:
            # unbuffered
            if self.ready_receivers:
                ready_receiver: Future[Any] = self.ready_receivers.popleft()
                ready_receiver.set_result(value)

            else:
                ready_producer: Future[Any] = asyncio.Future()
                new_producer = ProducerComponent(ready_producer, value)

                self.ready_producers.append(new_producer)
                return ready_producer

    async def pull(self) -> None | Any:

        # unbuffered
        if self.bound is not None:
            if self.ready_producers:
                producer_component: ProducerComponent = self.ready_producers.popleft()
                ready_producer: Future[Any] = producer_component.producer
                ready_producer.set_result(None)
                return producer_component.value
            else:
                ready_receiver: Future[Any] = asyncio.Future()
                self.ready_receivers.append(ready_receiver)
                return ready_receiver
