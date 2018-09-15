"""
The return value from ``dispatch`` is a response object.

    >>> response = methods.dispatch(request)
    >>> response
    {'jsonrpc': '2.0', 'result': 'foo', 'id': 1}

Use ``str()`` to get a JSON-encoded string::

    >>> str(response)
    '{"jsonrpc": "2.0", "result": "foo", "id": 1}'

There's also an HTTP status code if you need it::

    >>> response.http_status
    200

Response
    NotificationResponse
    BatchResponse - a list
    DictResponse - a dict
        SuccessResponse
        ErrorResponse
            InvalidJSONResponse
            InvalidJSONRPCResponse
            MethodNotFoundResponse
            InvalidParamsResponse
            ExceptionResponse
"""
import json
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, Optional

from . import status


# Sentinel to indicate nothing passed. We can't use the conventional None default value,
# because None (null) is valid JSON.
UNSPECIFIED = object()


class Response:
    """Base class of all responses."""

    # This basically means you don't need to do isinstance(NotificationResponse). All
    # responses are responding to a "request" (with an id attribute), except for
    # NotificationResponse
    is_request = True

    def __init__(self, http_status: Optional[int] = None) -> None:
        self.http_status = http_status


class NotificationResponse(Response):
    """
    Notification response.

    Returned from processing a successful `notification
    <http://www.jsonrpc.org/specification#notification>`_ (i.e. a request with
    no ``id`` member).
    """

    # This is the only notification response
    is_request = False

    def __init__(self, http_status: int = status.HTTP_NO_CONTENT) -> None:
        super().__init__(http_status=http_status)

    def __str__(self) -> str:
        return ""


class BatchResponse(Response, list):
    """
    Returned from batch requests.

    Basically a collection of responses.
    """

    def __init__(self, http_status: int = status.HTTP_OK) -> None:
        super().__init__(http_status=http_status)

    def __str__(self) -> str:
        """JSON-RPC response string."""
        return json.dumps(self)


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

    def __init__(
        self, *args, request_id: Optional[Any] = UNSPECIFIED, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.request_id = request_id

    def __str__(self):
        # Abstract.
        pass


class SuccessResponse(DictResponse):
    """
    Success Response returned from a Request.

    Returned from processing a successful request with an ``id`` member,
    (indicating that a payload is expected back).
    """

    def __init__(
        self, result: Any, request_id: Any, http_status: int = status.HTTP_OK
    ) -> None:
        """
        Args:
            request_id: Matches the original request's id value.
            result:
                The payload from processing the request. If the request was a
                JSON-RPC notification (i.e. the request id is ``None``), the result
                must also be ``None`` because notifications don't require any data
                returned.
            http_status: 
        """
        super().__init__(http_status=http_status)
        self.result = result
        self.request_id = request_id

    def __str__(self) -> str:
        """Use str() to get the JSON-RPC response string."""
        response = {"jsonrpc": "2.0", "result": self.result, "id": self.request_id}
        return json.dumps(sort_dict_response(response))


class ErrorResponse(DictResponse):
    """
    Error response.

    Returned if there was an error while processing the request.
    """

    def __init__(
        self,
        code: int,
        message: str,
        *args: Any,
        data: Any = UNSPECIFIED,
        debug: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Args:
            code: A Number that indicates the error type that occurred. This MUST be an
                integer.
            message: A string providing a short description of the error, eg.  "Invalid
                params".
            data: A Primitive or Structured value that contains additional information
                about the error. This may be omitted.
            debug: 
            http_status: The recommended HTTP status code.
            request_id: Must be the same as the value as the id member in the Request
                Object. If there was an error in detecting the id in the Request object
                (e.g. Parse error/Invalid Request), it MUST be Null.
        """
        super().__init__(*args, **kwargs)
        self.code = code
        self.message = message
        self.data = data
        self.debug = debug

    def __str__(self) -> str:
        """Use str() to get the JSON-RPC response string."""
        response = {
            "jsonrpc": "2.0",
            "error": {"code": self.code, "message": self.message},
        }  # type: Dict[str, Any]
        if self.request_id is not UNSPECIFIED:
            response["id"] = self.request_id
        if self.data is not UNSPECIFIED and self.debug:
            response["error"]["data"] = self.data
        return json.dumps(sort_dict_response(response))


class InvalidJSONResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_BAD_REQUEST, **kwargs: Any
    ) -> None:
        super().__init__(
            status.JSONRPC_PARSE_ERROR_CODE,
            "Invalid JSON",
            *args,
            http_status=http_status,
            **kwargs,
        )


class InvalidJSONRPCResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_BAD_REQUEST, **kwargs: Any
    ) -> None:
        super().__init__(
            status.JSONRPC_INVALID_REQUEST_CODE,
            "Invalid JSON-RPC",
            *args,
            http_status=http_status,
            **kwargs,
        )


class MethodNotFoundResponse(ErrorResponse):
    def __init__(
        self, *args: Any, http_status: int = status.HTTP_NOT_FOUND, **kwargs: Any
    ) -> None:
        super().__init__(
            status.JSONRPC_METHOD_NOT_FOUND_CODE,
            "Method not found",
            *args,
            http_status=http_status,
            **kwargs,
        )


class InvalidParamsResponse(ErrorResponse):
    def __init__(
        self,
        method,
        *args: Any,
        http_status: int = status.HTTP_BAD_REQUEST,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            status.JSONRPC_INVALID_PARAMS_CODE,
            "Invalid params to {}".format(method),
            *args,
            http_status=http_status,
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
            -32000,
            "Server error",
            *args,
            data=f"{exc.__class__.__name__}: {str(exc)}",
            http_status=http_status,
            **kwargs,
        )
