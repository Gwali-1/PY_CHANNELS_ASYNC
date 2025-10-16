# pychanasync

`pychanasync` is a lightweight python package which brings _Go-style_ channels to
python's _asyncio_ concurrency world. It is an async channel implementation,
providing a channel shaped tool for your channel shaped problems.

It allows for safe, easy and efficient communication between **coroutines**
scheduled on an event loop by providing a medium through which items/messages
can be pushed into from one end and pulled from the other as opposed to
sharing memory.

`pychanasync`is implemented entirely around pythons asyncio event loop.
The implementation is lock free ,taking advantage of the single threaded
cooperative concurrency model.

It is designed and implemented to work with coroutines and not threads, providing
safe and deterministic communication patterns without blocking the event loop.

pychanasync is built on the idea of

_"Don't communicate by sharing memory; share memory by communicating"_

The point was to implement a package tool that allow coroutines to exchange
messages instead of going the shared mutable state and locks route.

So if you are working on async program that fits the producer-consumer pattern or
are tackles channel shaped problems, `pychanasync` is highly recommended.

It makes async program easy to reason about and cleaner!

As mentioned , pychanasync is inspired by channels in Go but blends it with
Pythonic conventions. It provides clean, high level abstractions to pass messages
between coroutines and other features that feel naturally python.

- Buffered and unbuffered channel behaviour - _use either synchronous or buffered communication_
- Async iteration over channels - _Consume messages from a channel using `async for` loops._
- Context manager support - _Close channels and release resources when done with `async with`._
- Blocking/ awaitable operations - _`await chan.push(value)` and `await chan.pull()`
  for safe, cooperative communication._
  -Non-blocking operations - _`chan.push_nowait(value)` and `chan.pull_nowait()` for buffered channels when you don’t want to suspend._
- Select-like utility - _wait on multiple channel operations concurrently, similar to Go’s select statement, but in a clean and Pythonic way_

## installation

pychanasync is available on [PyPi](#)

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

Channels can be both buffered and unbuffered.

**unbuffered** channels have no internal buffer capacity. What this means is
every producer (`push`) will be block/suspend until there is a ready consumer on
the other end of the channel (`pull`) and every consumer until there is a
ready producer on the other end of the channel.

Communication happens synchronously. Both sender and receiver must be present
until any operation is completed.

This is great in scenarios where you want to properly synchronize operation of two components.
ensuring one can only proceed if the other acknowledges them.

```python
from pychanasync import channel

#create unbuffered channel
ch = Channel()

# send
async ch.push("item")

# receive
value = async ch.pull()

```

**buffered** channels has an internal buffer capacity and can hold a fixed
number of items at a time. When doing a `push` into a buffered channel, the
operation will only block when the buffer is full and until there is available
space to send the new item. Other than that the operation completes
and returns quickly.

On the other hand when you pull from a buffered channel , the operation will
only block or be suspended when the buffer is empty, until there are items
available in the buffer. Other than that the operation completes and returns quickly.

Here, unlike unbuffered channels , both senders and receivers don't have to be in sync. The communication
is asynchronous up to the buffers capacity limit.

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
        except Channel.Closed:
            break

async def main():
    ch = Channel(buffer=2)
    await asyncio.gather(producer(ch), consumer(ch))

asyncio.run(main())

```

_The code above follows typical structure of asynchronous code in asyncio. Here
we try to implement a simple producer which is a coroutine function that that
loops and sends a message into a buffered channel. We have another coroutine
function which continously reads from the buffered channel until it closes.
Both coroutine are scheduled to run on the event-loop to run using asyncio.gather_

It's evident how pychanasync faciltates the implementation of this pattern. you could have coroutines decoupled in their operation
and still have a means of easy communication in a clean concise manner.

One thing wort noting in this example is after the producer pushes the second item , it
waits until the consumer pulls an item before continuing . it does this seamlessly by suspending and resuming
on the event loop in a cooperative manner just as a task is supposed to behave . pychanasync does not get in
the way of

# Explain behaviour on channel closing on buffered and unbuffered and also lock free implementation

## Features

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

When the async-with block exits , the channel is closed automatically.

### Non-blocking channel operations

pychanasync provides non blocking variants of push and pull on buffered channels.
In this case , the coroutine will not block or suspend like the normal methods.

These methods will raise exceptions when the operation cannot proceed immediately

## exampls with other featurs - iteration , contexct manager , nowait select Async

## Reference - methods and properties

## Contributing and Development

## Setting up a dev environment

## Running tests

## Style guide and contribution guidelines

## semantic details
