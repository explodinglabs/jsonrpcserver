"""The response data types.

https://www.jsonrpc.org/specification#response_object
"""
from typing import Any, Dict, List, NamedTuple, Union

from returns.result import Result, Failure

from .codes import (
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
    ERROR_SERVER_ERROR,
)
from .sentinels import NODATA

Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]


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


Response = Result[SuccessResponse, ErrorResponse]


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


def serialize_error(response: ErrorResponse) -> Dict[str, Any]:
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


def serialize_success(response: SuccessResponse) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "result": response.result, "id": response.id}


def to_serializable_one(response: Response) -> Union[Deserialized, None]:
    return (
        serialize_error(response.failure())
        if isinstance(response, Failure)
        else serialize_success(response.unwrap())
    )


def to_serializable(response: Response) -> Union[Deserialized, None]:
    if response is None:
        return None
    elif isinstance(response, List):
        return [to_serializable_one(r) for r in response]
    else:
        return to_serializable_one(response)
