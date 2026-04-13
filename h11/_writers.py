# Code to read HTTP data
#
# Strategy: each writer takes an event + a write-some-bytes function, which is
# calls.
#
# WRITERS is a dict describing how to pick a reader. It maps states to either:
# - a writer
# - or, for body writers, a dict of framin-dependent writer factories

from typing import Any, Callable, Dict, List, Tuple, Type, Union

from ._events import Data, EndOfMessage, Event, InformationalResponse, Request, Response
from ._headers import Headers
from ._state import CLIENT, IDLE, SEND_BODY, SEND_RESPONSE, SERVER
from ._util import LocalProtocolError, Sentinel

__all__ = ["WRITERS"]

Writer = Callable[[bytes], Any]


def write_headers(headers: Headers, write: Writer) -> None:
    # "Since the Host field-value is critical information for handling a
    # request, a user agent SHOULD generate Host as the first header field
    # following the request-line." - RFC 7230
    pass


def write_request(request: Request, write: Writer) -> None:
    pass


# Shared between InformationalResponse and Response
def write_any_response(
    response: Union[InformationalResponse, Response], write: Writer
) -> None:
    pass


class BodyWriter:
    def __call__(self, event: Event, write: Writer) -> None:
        if type(event) is Data:
            self.send_data(event.data, write)
        elif type(event) is EndOfMessage:
            self.send_eom(event.headers, write)
        else:  # pragma: no cover
            assert False

    def send_data(self, data: bytes, write: Writer) -> None:
        pass

    def send_eom(self, headers: Headers, write: Writer) -> None:
        pass


#
# These are all careful not to do anything to 'data' except call len(data) and
# write(data). This allows us to transparently pass-through funny objects,
# like placeholder objects referring to files on disk that will be sent via
# sendfile(2).
#
class ContentLengthWriter(BodyWriter):
    def __init__(self, length: int) -> None:
        self._length = length

    def send_data(self, data: bytes, write: Writer) -> None:
        pass

    def send_eom(self, headers: Headers, write: Writer) -> None:
        pass


class ChunkedWriter(BodyWriter):
    def send_data(self, data: bytes, write: Writer) -> None:
        # if we encoded 0-length data in the naive way, it would look like an
        # end-of-message.
        pass

    def send_eom(self, headers: Headers, write: Writer) -> None:
        pass


class Http10Writer(BodyWriter):
    def send_data(self, data: bytes, write: Writer) -> None:
        pass

    def send_eom(self, headers: Headers, write: Writer) -> None:
        pass
        # no need to close the socket ourselves, that will be taken care of by
        # Connection: close machinery


WritersType = Dict[
    Union[Tuple[Type[Sentinel], Type[Sentinel]], Type[Sentinel]],
    Union[
        Dict[str, Type[BodyWriter]],
        Callable[[Union[InformationalResponse, Response], Writer], None],
        Callable[[Request, Writer], None],
    ],
]

WRITERS: WritersType = {
    (CLIENT, IDLE): write_request,
    (SERVER, IDLE): write_any_response,
    (SERVER, SEND_RESPONSE): write_any_response,
    SEND_BODY: {
        "chunked": ChunkedWriter,
        "content-length": ContentLengthWriter,
        "http/1.0": Http10Writer,
    },
}
