"""The response data types.

https://www.jsonrpc.org/specification#response_object
"""

from typing import Any, Dict, List, NamedTuple, Union

from returns.result import Failure, Result

from .codes import (
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
    ERROR_SERVER_ERROR,
)
from .sentinels import NODATA

Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]


class SuccessResponse(NamedTuple):
    """It would be nice to subclass Success here, adding only id. But it's not possible
    to easily subclass NamedTuples in Python 3.6. (I believe it can be done in 3.8.)
    """

    result: Any
    id: Any


class ErrorResponse(NamedTuple):
    """It would be nice to subclass Error here, adding only id. But it's not possible to
    easily subclass NamedTuples in Python 3.6. (I believe it can be done in 3.8.)
    """

    code: int
    message: str
    data: Any
    id: Any


Response = Result[SuccessResponse, ErrorResponse]


def ParseErrorResponse(data: Any) -> ErrorResponse:
    """An ErrorResponse with most attributes already populated.

    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(ERROR_PARSE_ERROR, "Parse error", data, None)


def InvalidRequestResponse(data: Any) -> ErrorResponse:
    """An ErrorResponse with most attributes already populated.

    From the spec: "This (id) member is REQUIRED. It MUST be the same as the value of
    the id member in the Request Object.  If there was an error in detecting the id in
    the Request object (e.g. Parse error/Invalid Request), it MUST be Null."
    """
    return ErrorResponse(ERROR_INVALID_REQUEST, "Invalid request", data, None)


def MethodNotFoundResponse(data: Any, id: Any) -> ErrorResponse:
    """An ErrorResponse with some attributes already populated."""
    return ErrorResponse(ERROR_METHOD_NOT_FOUND, "Method not found", data, id)


def ServerErrorResponse(data: Any, id: Any) -> ErrorResponse:
    """An ErrorResponse with some attributes already populated."""
    return ErrorResponse(ERROR_SERVER_ERROR, "Server error", data, id)


def to_error_dict(response: ErrorResponse) -> Dict[str, Any]:
    """From ErrorResponse object to dict"""
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


def to_success_dict(response: SuccessResponse) -> Dict[str, Any]:
    """From SuccessResponse object to dict"""
    return {"jsonrpc": "2.0", "result": response.result, "id": response.id}


def to_dict(response: Response) -> Dict[str, Any]:
    """Serialize either an error or success response object to dict"""
    return (
        to_error_dict(response.failure())
        if isinstance(response, Failure)
        else to_success_dict(response.unwrap())
    )


def to_serializable(
    response: Union[Response, List[Response], None],
) -> Union[Deserialized, None]:
    """Serialize a response object (or list of them), to a dict, or list of them."""
    if response is None:
        return None
    if isinstance(response, List):
        return [to_dict(r) for r in response]
    return to_dict(response)
