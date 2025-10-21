[![Run Tests](https://github.com/Gwali-1/PY_CHANNELS_ASYNC/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/Gwali-1/PY_CHANNELS_ASYNC/actions/workflows/test-and-lint.yml)

# Pychanasync

`pychanasync` is a lightweight python package which brings _Go-style_ channels to
python's _asyncio_ concurrency world. It is an async-channel implementation,
providing a channel shaped tool for channel shaped problems.

`pychanasync` is implemented entirely around pythons asyncio event loop.
The implementation is **lock free** ,taking advantage of the _single threaded
cooperative_ concurrency model.

It is designed and implemented to work with coroutines and **not threads**, providing
safe and deterministic communication patterns without blocking the event loop.

Visit [documentation](https://gwali-1.github.io/PY_CHANNELS_ASYNC/) site for more details.

## Features

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

## Quickstart

Channels can be both **buffered** and **unbuffered**.

**unbuffered** channels have no internal buffer capacity. What this means is
every producer (`push`) will block/suspend until there is a ready consumer on
the other end of the channel (`pull`) and every consumer until there is a
ready producer on the other end of the channel.

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

Below is a buffered channel that can hold 300 items at a time.

```python
from pychanasync import channel

ch = Channel(buffer=300)

# send
async ch.push("item")

# receive
value = async ch.pull()

```

### Async Iteration

pychanasync supports async iteration, allowing you to consume items from a channel
in a clean way using `async for loop`.

We can rewrite our consumer above as

```python

async def consumer(ch):
    async for msg in ch:
        print(f"Received: {msg}")

```

Once the producer closes the channel , the iteration ends .

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

When the `async-with` block exits , the channel is closed automatically.

### Chanselect

The `chanselect` utility method allows you to start and wait on multiple channel operations simultaneously,
returning the one that completes first.

**synthax**

```python

    chan, value = await chanselect(
        (chan_a, chan_a.pull()),
        (chan_b, chan_b.pull())
    )

```

checkout more [features](https://gwali-1.github.io/PY_CHANNELS_ASYNC/#features)

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
        except Channel.Closed:
            break

async def main():
    ch = Channel(buffer=2)
    await asyncio.gather(producer(ch), consumer(ch))

asyncio.run(main())

```

### Contributing

To contribute or set up the project locally.

find the project source code on [github](https://github.com/Gwali-1/PY_CHANNELS_ASYNC)

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
