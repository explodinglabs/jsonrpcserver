"""
Responses.

The return value from `dispatch` is a Response object.

    >>> response = dispatch(request)
    >>> response.result
    'foo'

Use `str()` to get a JSON-encoded string::

    >>> str(response)
    '{"jsonrpc": "2.0", "result": "foo", "id": 1}'

There's also an HTTP status code if you need it::

    >>> response.http_status
    200

Response heirarchy:

    NotificationResponse
    DictResponse - a dict
        SuccessResponse
        ErrorResponse
            InvalidJSONResponse
            InvalidJSONRPCResponse
            MethodNotFoundResponse
            InvalidParamsResponse
            ExceptionResponse
    BatchResponse - a list of DictResponses
"""
import json
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Iterable, Optional, cast

from . import status

UNSPECIFIED = object()


class Response(ABC):
    """Base class of all responses."""

    def __init__(self, http_status: Optional[int] = None) -> None:
        self.http_status = http_status

    @property
    @abstractmethod
    def wanted(self) -> bool:
        """
        Indicates that this response is wanted by the request; the request had an "id"
        member, and was therefore not a JSON-RPC Notification object. All responses are
        wanted, except NotificationResponse.

        Note that blocking/synchronous transfer protocols require a response to every
        request no matter what, in which case this property should be ignored and
        str(response) returned regardless.
        """


class NotificationResponse(Response):
    """
    Notification response.

    Returned from processing a successful
    [notification](http://www.jsonrpc.org/specification#notification) (i.e. a request
    with no `id` member).
    """

    def __init__(self, http_status: int = status.HTTP_NO_CONTENT) -> None:
        super().__init__(http_status=http_status)

    @property
    def wanted(self) -> bool:
        return False

    def __str__(self) -> str:
        return ""


def sort_dict_response(response: Dict[str, Any]) -> OrderedDict:
    """
    Sort the keys of a dict, returning an OrderedDict.

    This has no effect other than making it nicer to read. It's also only useful with
    Python 3.5, since from 3.6 onwards, dictionaries hold their order.

    Args:
        response: The JSON-RPC response to sort.

    Returns:
        The same response, sorted as an OrderedDict.

    Examples:
        >>> json.dumps(sort_dict_response({'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
        {"jsonrpc": "2.0", "result": 5, "id": 1}
    """
    root_order = ["jsonrpc", "result", "error", "id"]
    error_order = ["code", "message", "data"]
    req = OrderedDict(sorted(response.items(), key=lambda k: root_order.index(k[0])))
    if "error" in response:
        req["error"] = OrderedDict(
            sorted(response["error"].items(), key=lambda k: error_order.index(k[0]))
        )
    return req


class DictResponse(Response):
    """Abstract..."""

    def __init__(self, *args: Any, id: Any, **kwargs: Any) -> None:
        """
        Args:
            id: Must be the same as the value as the id member in the Request Object. If
                there was an error in detecting the id in the Request object (e.g. Parse
                error/Invalid Request), it MUST be Null.
        """
        super().__init__(*args, **kwargs)
        self.id = id

    @property
    def wanted(self) -> bool:
        return True

    @abstractmethod
    def deserialized(self) -> dict:
        """Gets the response as a dictionary. Used by __str__."""

    def __str__(self) -> str:
        """Use str() to get the JSON-RPC response string."""
        return json.dumps(sort_dict_response(self.deserialized()))


class SuccessResponse(DictResponse):
    """
    Success response returned from a request.

    Returned from processing a successful request with an `id` member indicating that a
    result payload is expected back.
    """

    def __init__(
        self, result: Any, *, http_status: int = status.HTTP_OK, **kwargs: Any
    ) -> None:
        """
        Args:
            result:
                The payload from processing the request. If the request was a JSON-RPC
                notification (i.e. the request id is `None`), the result must also be
                `None` because notifications don't require any data returned.
            http_status: 
        """
        super().__init__(http_status=http_status, **kwargs)
        self.result = result

    def deserialized(self) -> dict:
        return {"jsonrpc": "2.0", "result": self.result, "id": self.id}


class ErrorResponse(DictResponse):
    """
    Error response.

    Returned if there was an error while processing the request.
    """

    def __init__(
        self,
        message: str,
        *args: Any,
        code: int,
        data: Any = UNSPECIFIED,
        debug: bool,  # required, named
        **kwargs: Any,
    ) -> None:
        """
        Args:
            message: A string providing a short description of the error, eg.  "Invalid
                params".
            code: A Number that indicates the error type that occurred. This MUST be an
                integer.
            data: A Primitive or Structured value that contains additional information
                about the error. This may be omitted.
            debug: Include more (possibly sensitive) information in the response.
        """
        super().__init__(*args, **kwargs)
        self.code = code
        self.message = message
        self.data = data
        self.debug = debug

    def deserialized(self) -> dict:
        dct = {
            "jsonrpc": "2.0",
            "error": {"code": self.code, "message": self.message},
            "id": self.id,
        }  # type: Dict[str, Any]
        if self.data is not UNSPECIFIED and self.debug:
            dct["error"]["data"] = self.data
        return dct


class InvalidJSONResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_BAD_REQUEST, **kwargs: Any
    ) -> None:
        super().__init__(
            "Invalid JSON",
            code=status.JSONRPC_PARSE_ERROR_CODE,
            http_status=http_status,
            # Must include an id in error responses, but it's impossible to retrieve
            id=None,
            *args,
            **kwargs,
        )
        assert self.id is None


class InvalidJSONRPCResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_BAD_REQUEST, **kwargs: Any
    ) -> None:
        super().__init__(
            "Invalid JSON-RPC",
            code=status.JSONRPC_INVALID_REQUEST_CODE,
            http_status=http_status,
            # Must include an id in error responses, but it's impossible to retrieve
            id=None,
            *args,
            **kwargs,
        )
        assert self.id is None


class MethodNotFoundResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_NOT_FOUND, **kwargs: Any
    ) -> None:
        super().__init__(
            "Method not found",
            code=status.JSONRPC_METHOD_NOT_FOUND_CODE,
            http_status=http_status,
            *args,
            **kwargs,
        )


class InvalidParamsResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_BAD_REQUEST, **kwargs: Any
    ) -> None:
        super().__init__(
            "Invalid parameters",
            code=status.JSONRPC_INVALID_PARAMS_CODE,
            http_status=http_status,
            *args,
            **kwargs,
        )


class ExceptionResponse(ErrorResponse):
    def __init__(
        self,
        exc: BaseException,
        *args: Any,
        http_status: int = status.HTTP_INTERNAL_ERROR,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            "Server error",
            code=-32000,
            data=f"{exc.__class__.__name__}: {str(exc)}",
            http_status=http_status,
            *args,
            **kwargs,
        )


class BatchResponse(Response):
    """
    Returned from batch requests.

    A collection of Responses, either success or error.
    """

    def __init__(
        self, responses: Iterable[Response], http_status: int = status.HTTP_OK
    ) -> None:
        super().__init__(http_status=http_status)
        # Remove notifications; these are not allowed in batch responses
        self.responses = cast(
            Iterable[DictResponse], {r for r in responses if r.wanted}
        )

    @property
    def wanted(self) -> bool:
        return True

    def deserialized(self) -> list:
        return [r.deserialized() for r in self.responses]

    def __str__(self) -> str:
        """JSON-RPC response string."""
        dicts = self.deserialized()
        # For an all-notifications response, an empty string should be returned, as per
        # spec
        return json.dumps(dicts) if len(dicts) else ""
