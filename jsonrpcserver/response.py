"""
response.py - the response data types.

Methods return a Result, but internally, the Result is converted to a Response type -
either a SuccessResponse or ErrorResponse. These simply add the id that's associated
with the original request.

>>> dispatch('{"jsonrpc": "2.0", "method": "ping", params: [], "id": 1}', [my_method])
SuccessResponse(result='pong', id=1)

Use to_serializable to get a dictionary or list containing the JSON-RPC response
elements, and then serialize it to JSON:

>>> json.dumps(to_serializable(Right(SuccessResponse(result='foo', id=1))))
'{"jsonrpc": "2.0", "result": "foo", "id": 1}'
"""
from typing import Any, List, Type, NamedTuple, Union

from oslash.either import Either, Left  # type: ignore

from .codes import (
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
    ERROR_SERVER_ERROR,
)
from .result import NODATA


class SuccessResponse(NamedTuple):
    """
    It would be nice to subclass Success here, adding only id. But it's not possible to
    easily subclass NamedTuples in Python 3.6. (I believe it can be done in 3.8.)
    """

    result: str
    id: Any


class ErrorResponse(NamedTuple):
    """
    It would be nice to subclass Error here, adding only id. But it's not possible to
    easily subclass NamedTuples in Python 3.6. (I believe it can be done in 3.8.)
    """

    code: int
    message: str
    data: Any
    id: Any


Response = Type[Either[ErrorResponse, SuccessResponse]]


def ParseErrorResponse(data: Any) -> ErrorResponse:
    """
    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(ERROR_PARSE_ERROR, "Parse error", data, None)


def InvalidRequestResponse(data: Any) -> ErrorResponse:
    """
    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(ERROR_INVALID_REQUEST, "Invalid request", data, None)


def MethodNotFoundResponse(data: Any, id: Any) -> ErrorResponse:
    return ErrorResponse(ERROR_METHOD_NOT_FOUND, "Method not found", data, id)


def ServerErrorResponse(data: Any, id: Any) -> ErrorResponse:
    return ErrorResponse(ERROR_SERVER_ERROR, "Server error", data, id)


def serialize_error(response: ErrorResponse) -> dict:
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": response.code,
            "message": response.message,
            # "data" may be omitted.
            **({"data": response.data} if response.data is not NODATA else {}),
        },
        "id": response.id,
    }


def serialize_success(response: SuccessResponse) -> dict:
    return {"jsonrpc": "2.0", "result": response.result, "id": response.id}


def to_serializable_one(response: Either[ErrorResponse, SuccessResponse]) -> dict:
    return (
        serialize_error(response._error)
        if isinstance(response, Left)
        else serialize_success(response._value)
    )


def to_serializable(
    response: Union[Response, List[Response], None]
) -> Union[dict, List[dict], None]:
    """Converts a Response to a JSON-RPC response dict."""
    if response is None:
        return None
    elif isinstance(response, list):
        return [to_serializable_one(r) for r in response]
    else:
        return to_serializable_one(response)
