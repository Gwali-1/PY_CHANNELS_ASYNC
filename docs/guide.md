# pychanasync

pychanasync is a async channel implementation in python giving you a channel shaped solutions for channel shaped problems.
Basically it combines the Go channel like behaviour with pythonic conventions and abstractions simplifying the implementation of
async programs by exposing simple APIs to allow communication or message passing between coroutines ,

pychanasync is a lightweight python library which introduces Go-style channels to python's
asyncio concurrency world. It allows safe , easy and efficient communication between coroutines
scheduled on an event loop by providing a medium through which messages can be pushed into
and pulled from as opposed to sharing memory between them and synchronizing access with locks.

pychanasync allows a synchronizing point between producers and consumers , letting them recieve and send
values in both a synchronous and asynchronous nature in the natural , declarative way python provides using
aync and await model.

pychanasync is implemented entirely around pythons asyncio concurrency model thus the evnt loop operation semantics and
the single threaded cooperative nature.
It is designed and implemented to work with coroutines and not threads. It follows the rules of the asyncio event loop
providing a safe and deterministic communication patterns without blocking the event loop.

every send `await chan.push(value)` and recieve operation `await chan.pull()` integrates with the asyncio scheduling ,
task suspension and resumption mechanism ensuring that it does not get in the way and allows the runtime to manage
concurrency efficienly .

As mentioned , pychanasync is inspired by channels in Go but it combines this behaviour with Pythonic conventions and
async patterns providing featues like:

- Buffered and unbuffered channel behaviour
- Async iteration over channels
- Context manager support for resource cleanup , in this case closing the channel
- Select like utility allowing to intiate and wait on multiple channel operations in a clean concise way

## installation

## Basic Usage , creating , sending , receiving from channel

## exampls with other featurs - iteration , contexct manager , nowait select Async

## Reference - methods and properties

## Contributing and Development

## Setting up a dev environment

## Running tests

## Style guide and contribution guidelines

## semantic details
