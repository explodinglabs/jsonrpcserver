"""
response.py - the response data types.

Methods return a Result, but internally, the Result is converted to a Response type -
either a SuccessResponse or ErrorResponse. These simply add the id that's associated
with the original request.

>>> dispatch('{"jsonrpc": "2.0", "method": "ping", params: [], "id": 1}', [my_method])
SuccessResponse(result='pong', id=1)

Use to_serializable to get a dictionary or list containing the JSON-RPC response
elements, and then serialize it to JSON:

>>> json.dumps(to_serializable(SuccessResponse(result='foo', id=1)))
'{"jsonrpc": "2.0", "result": "foo", "id": 1}'
"""
from typing import Any, List, NamedTuple, Union

from . import status
from .request import NOID
from .result import Result, Success, UNSPECIFIED


class SuccessResponse(NamedTuple):
    """
    It would be nice to subclass Success here, adding only id. But it's not possible to
    easily subclass NamedTuples in Python 3.6. (I believe it can be done in 3.8.)
    """

    result: str
    id: Any


class ErrorResponse(NamedTuple):
    code: int
    message: str
    data: Any
    id: Any


# Union of the two valid response types
Response = Union[SuccessResponse, ErrorResponse]


def ParseErrorResponse(data: Any) -> ErrorResponse:
    """
    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(status.JSONRPC_PARSE_ERROR_CODE, "Parse error", data, None)


def InvalidRequestResponse(data: Any) -> ErrorResponse:
    """
    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(
        status.JSONRPC_INVALID_REQUEST_CODE, "Invalid request", data, None
    )


def MethodNotFoundResponse(data: Any, id: Any) -> ErrorResponse:
    return ErrorResponse(
        status.JSONRPC_METHOD_NOT_FOUND_CODE, "Method not found", data, id
    )


def ServerErrorResponse(data: Any, id: Any) -> ErrorResponse:
    return ErrorResponse(status.JSONRPC_SERVER_ERROR_CODE, "Server error", data, id)


def from_result(result: Result, id: Any) -> Union[Response, None]:
    """Converts a Result to a Response (by adding the request id)."""
    if id is NOID:  # Response can't be a notification.
        return None
    elif isinstance(result, Success):
        return SuccessResponse(**result._asdict(), id=id)
    else:
        return ErrorResponse(**result._asdict(), id=id)


def to_serializable_one(response: Response) -> dict:
    if isinstance(response, ErrorResponse):
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": response.code,
                "message": response.message,
                # "data" may be omitted.
                **({"data": response.data} if response.data is not UNSPECIFIED else {}),
            },
            "id": response.id,
        }
    else:  # isinstance(response, SuccessResponse):
        return {"jsonrpc": "2.0", "result": response.result, "id": response.id}


def to_serializable(
    response: Union[Response, List[Response]]
) -> Union[dict, List[dict]]:
    """Converts a Response to a JSON-RPC response dict."""
    if isinstance(response, list):
        return [to_serializable_one(r) for r in response]
    else:
        return to_serializable_one(response)
