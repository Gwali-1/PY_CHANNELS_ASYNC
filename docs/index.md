# pychanasync

`pychanasync` is a lightweight python package which brings _Go-style_ channels to
python's _asyncio_ concurrency world. It is an async-channel implementation,
providing a channel shaped tool for channel shaped problems.

It allows for safe, easy and efficient communication between **coroutines**
scheduled on the asyncio event loop by providing a medium through which items/messages
can be pushed into from one end and pulled from the other sequentially as opposed to
sharing memory.

`pychanasync` is implemented entirely around pythons asyncio event loop.
The implementation is **lock free** ,taking advantage of the _single threaded
cooperative_ concurrency model.

It is designed and implemented to work with coroutines and **not threads**, providing
safe and deterministic communication patterns without blocking the event loop.

`pychanasync` is built on the idea;

_"Don't communicate by sharing memory; share memory by communicating"_

---

The point was to implement a package tool that allow coroutines to exchange
messages instead of going the shared mutable state and locks route.

So if you are working on async program in python which fits the producer-consumer pattern or
need a channel shaped solution, `pychanasync` is highly recommended.

**It makes async programs cleaner and easy to reason about!**

---

As mentioned , pychanasync is inspired by channels in [Go](https://go101.org/article/channel.html)
but blends it with Pythonic conventions. It provides clean, high level abstractions to pass messages
between coroutines/tasks and other features that feel naturally python.

- **Buffered and unbuffered channel semantics** - _use either synchronous or buffered communication_
- **Async iteration over channels** - _Consume messages from a channel using `async for` loops._
- **Context manager support** - _close channels and release resources when done with `async with`._
- **Blocking/ awaitable operations** - _`await chan.push(value)` and `await chan.pull()`
  for safe, cooperative communication._
- **Non-blocking operations** - _`chan.push_nowait(value)` and `chan.pull_nowait()` for buffered channels when you don’t want to suspend._
- **Select-like utility** - _wait on multiple channel operations concurrently, similar to Go’s select statement, in a clean and Pythonic way_

## Installation

pychanasync is available on [PyPi](https://pypi.org/project/pychanasync/)

```shell
pip install pychanasync
```

or you can install it from source

```shell
git clone https://github.com/Gwali-1/PY_CHANNELS_ASYNC
cd PY_CHANNELS_ASYNC
pip install -e .

```

## Quickstart

Channels can be both **buffered** and **unbuffered**.

**unbuffered** channels have no internal buffer capacity. What this means is
every producer (`push`) will block/suspend until there is a ready consumer on
the other end of the channel (`pull`) and every consumer until there is a
ready producer on the other end of the channel.

Communication happens synchronously. Both sender and receiver must be present
until any operation is completed.

This is great in scenarios where you want to properly **synchronize** operation of two components.
ensuring one can only proceed if the other acknowledges them.

```python
from pychanasync import channel

#create unbuffered channel
ch = Channel()

# send
async ch.push("item") #blocks here

# receive
value = async ch.pull()

```

**buffered** channels have an internal buffer capacity and can hold (**N**)
number of items at a time. When doing a `push` into a buffered channel, the
operation will only block when the buffer is full and until there is available
space to send the new item. Other than that the operation completes
and returns quickly.

On the other hand when you pull from a buffered channel , the operation will
only block or be suspended when the buffer is empty, until there are items
available in the buffer. Other than that the operation completes and returns and item
from the channel quickly.

Here, unlike **unbuffered** channels , both senders and receivers don't have to be in sync. The communication
is asynchronous up to the buffers capacity limit (**N**).

This is great in scenarios for example when you want a smooth outburst of work, decoupling producer
and consumer speed.

Below is a buffered channel that can hold 300 items at a time.

```python
from pychanasync import channel

ch = Channel(buffer=300)

# send
async ch.push("item")

# receive
value = async ch.pull()

```

## Basic consumer-producer example

```python

import asyncio
from pychanasync import Channel

async def producer(ch):
    for i in range(3):
        await ch.push(f"msg {i}")
        print(f"Sent msg {i}")
    ch.close()  # gracefully close when done

async def consumer(ch):
    while True:
        try:
            msg = await ch.pull()
            print(f"Received {msg}")
        except ChannelClosed:
            break

async def main():
    ch = Channel(buffer=2)
    await asyncio.gather(producer(ch), consumer(ch))

asyncio.run(main())

```

_The code above follows typical structure of asynchronous code in asyncio python. Here
we try to implement a simple producer which is a coroutine function that that
loops and sends a message into a buffered channel. We have another coroutine
function which continuously reads from the buffered channel until it is closed.
Both coroutines are scheduled to run on the event-loop using `asyncio.gather`_

**It’s clear how pychanasync makes this pattern easy to implement, allowing coroutines to remain decoupled in their
execution while still communicating seamlessly in a clean and concise way.**

One thing worth noting in this example is after the producer pushes the second item , it
waits until the consumer pulls an item before continuing . it does this seamlessly by suspending and resuming
on the event loop in a cooperative manner just as a task is supposed to behave . pychanasync does not get in
the way of the event loop.

You can find more practical code examples in the `pychanasync` [GitHub repository](https://github.com/Gwali-1/PY_CHANNELS_ASYNC/tree/main/Examples/Rob-Pike-Talk).  
It includes implementations of several concurrency patterns from [Rob Pike’s talk](https://youtu.be/f6kdp27TYZs).

These examples demonstrate how to model real-world coroutine coordination problems using `pychanasync`
such as fan-in , Generator pattern etc. Check it out.

## Features

### Async Iteration

pychanasync supports async iteration, allowing you to consume items from a channel
in a clean way using `async for` loop.

We can rewrite our consumer above as

```python

async def consumer(ch):
    async for msg in ch:
        print(f"Received: {msg}")

```

Once the producer closes the channel, the iteration ends .

### Context manager support

pychanasync has support for asynchronous context managers for automatic cleanup.

We can rewrite out producer component as

```python
async def producer(channel):
  async with channel  as ch:
    for i in range(3):
        await ch.push(f"msg {i}")
        print(f"Sent msg {i}")

```

When the `async-with` block exits, the channel is closed automatically.

### chanselect

The `chanselect` utility method allows you to start and wait on multiple channel operations simultaneously,
returning the one that **completes first**.

It behaves similarly to Go’s [select](https://gobyexample.com/select) statement.

The `chanselect` function takes **one or more tuples**, each containing a **channel** and a **channel operation**
(such as `chan.push(value)` or `chan.pull()`).

It concurrently waits on all provided operations and
returns the first one to complete.

The function returns a tuple depending on the type of operation that finished first:

- For `pull` operation, it returns (**channel, value**).
- For `push` operation, it returns (**channel, None**).

**synthax**

```python

    chan, value = await chanselect(
        (chan_a, chan_a.pull()),
        (chan_b, chan_b.pull())
    )

```

**Example**

```python
import asyncio
from pychanasync import Channel, chanselect

async def wait_and_push(chan, delay, item):
    await asyncio.sleep(delay)
    await chan.push(item)

async def main():
    chan_a = Channel(bound=2)
    chan_b = Channel(bound=2)
    chan_c = Channel(bound=2)

    asyncio.create_task(wait_and_push(chan_a, 0.01, "item_a"))
    asyncio.create_task(wait_and_push(chan_b, 0.05, "item_b"))
    asyncio.create_task(wait_and_push(chan_c, 0.02, "item_c"))

    chan, value = await chanselect(
        (chan_a, chan_a.pull()),
        (chan_b, chan_b.pull()),
        (chan_c, chan_c.pull())
    )

    if chan = chan_a:
        print(f"{value} was received from chan a ")

    if chan = chan_b:
        print(f"{value} was received from chan b ")

    if chan = chan_c:
        print(f"{value} was received from chan c ")

asyncio.run(main())

```

In the example above 3 channels are created and populated at different times.
The `chanselect` call waits for the first available value among the three.
It returns as soon as the first pull operation succeed which in this case is
chan_a

### Non-blocking channel operations

pychanasync provides non-blocking variants of `push` and `pull` on **buffered** channels.
In this case , the coroutine will not block or suspend.

These methods will raise exceptions when the operation cannot proceed immediately.

When you try to send an item with `push_nowait` into a buffered channel which is
full, it raises a `ChannelFull` exception.

When you try to pull an item with `push_nowait` from a buffered channel which is
empty, it raises a `ChannelEmpty` exception.

**push_nowait**

```python
ch = Channel(bound=2)

ch.push_nowait("A")
ch.push_nowait("B")

try:
    ch.push_nowait("C")
except ChannelFull:
    print("Buffer is full — could not push!")


```

**pull_nowait**

```python
try:
    value = ch.pull_nowait()
except ChannelEmpty:
    print("Buffer is empty — nothing to receive.")

```

## Channel closing behaviour

Closing the channel signals that no more items can be sent to it or read from it.
But what happens to already pending receive or send operations depends
on the type of channel.

**Buffered channel**

When you close a buffered channel, the internal buffer is drained. Any pending
readers will receive the items in the buffer at the time of closing. Once the buffer
is empty and there are more pending readers , They are woken up/terminated with
a `ChannelClosed` exceptions.

Also, all pending senders , thus those waiting to push into the channel but the buffer
was full are terminated with a `ChannelClosed` exception.

After closing, no new send or receive operations are allowed. Any attempt raises `ChannelClosed`.

**unbuffered channel**

For unbuffered channels ie those without a bound , closing the channel
immediately terminates all pending senders and receivers with a `ChannelClosed`

Because there’s no buffer to drain, no additional values are delivered after closing.

And as with buffered channels , no further operations can be performed after channel's closure.

## API Reference

#### await ch.push(val)

Will suspend until item can be sent (or buffer space is available)

#### await ch.pull()

Will suspend until value is available to be read.

#### ch.push_nowait(val)

Raises exception if buffer is full (**only for buffered channels**)

#### ch.pull_nowait(val)

Raises exception if buffer is empty (**only for buffered channels**)

#### ch.close()

Closes the channel and wakes up all waiting tasks/coroutines with pending channel operations.

#### ch.csize()

Return the number of items in the channel(None for unbuffered).

#### ch.full()

Returns True if there are maxsize items in the channel.

#### ch.empty()

Returns True if the channel is empty, False otherwise.

#### ch.closed

Returns True if the channel is closed.

### Contributing

To contribute or set up the project locally.

find the project source code on [GitHub](https://github.com/Gwali-1/PY_CHANNELS_ASYNC)

**Clone the project**

```shell
git clone https://github.com/Gwali-1/PY_CHANNELS_ASYNC
cd PY_CHANNELS_ASYNC
```

**Install dependencies**

```shell
pipenv install --dev

```

**Running tests**
From the project root

```shell

pipenv run pytest
```

**Installing the package locally**
From the project root

```shell
pip install -e .

```
