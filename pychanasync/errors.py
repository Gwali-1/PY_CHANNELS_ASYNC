class ChannelError(Exception):
    """
    Base exception class for Channel class. Represents all Channel
    related exceptions. Catching this is catching all exceptions thrown by a
    channel.
    """

    pass


class ChannelClosed(Exception):
    """
    ChannelClosed Exception thrown when a channel has been closed(usually by a producer)
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.which_chan: object = kwargs.pop("which_chan")
        super().__init__(*args, **kwargs)


class ChannelFull(Exception):
    """
    ChannelFull  exception  thrown when a channel(in this case buffered) is full, and
    producer does not want to wait.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.which_chan: object = kwargs.pop("which_chan")
        super().__init__(*args, **kwargs)


class ChannelEmpty(Exception):
    """
    ChannelEmpty  exception  thrown when a channel(in this case buffered) is empty, and
    receiver does not want to wait.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.which_chan: object = kwargs.pop("which_chan")
        super().__init__(*args, **kwargs)
