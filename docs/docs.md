# PY_CHANNELS_ASYNC

_An async-native python channel implementation._

_Providing a non blocking, coroutine friendly way for tasks to communicate and synchronize._

_Exposes APIs to facilitate concurrent task communication through message passing
like channels in Go._

_Works seamlessly with existing async await concurrency model in python (using asyncio)._

_Pipeline to stream data in a producer consumer pattern_

# commit point semantics

- A pull is complete only if an item is removed from the buffer in the case of buffered
  channel or if consumer is matched with ready
  producer to exchange item in the case of unbuffered channel

- A push is complete only if an item is appended to the buffer for buffered channel
  or producer is matched with ready receiver for unbuffered

All suspended producers/ consumers regardless of channel type are incomplete and
should receive `ChannelClosed` exception when you close
channel

# Closing channel semantics

- All suspended producers and consumers receive `ChannelClosed` exception.
- Drain out already appended items to ready consumers (in the case of buffered channel)
- Lock on the same lock for closing channel as well as push and pull operations to
  ensure atomic behaviour and enforce no appending or receiving after channel closed
