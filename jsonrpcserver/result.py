"""
The result data types - the results of calling a method.

Methods must return either a Success or Error result. A union type "Result"
combines the two result types.

    @method
    def my_method(request: Request) -> Result:

Success indicates success. Optionally pass a result value.

    return Success(result)

Error indicates failure.

    return Error(-1, "There was an error")

InvalidParams is a shortcut to this error response:

    return InvalidParams("Colour is invalid")

Which is equivalent to (-32602 is the Invalid Params error code in JSON-RPC):

    return Error(-32602, "Color is invalid")
"""
from typing import Any, NamedTuple, Optional, Union

from . import status

# This is used to indicate when a value isn't present. We use this instead of
# None, because None is a valid JSON-serializable type.
UNSPECIFIED = object()


class Success(NamedTuple):
    result: Optional[str] = None


class Error(NamedTuple):
    code: int
    message: str
    data: Any = UNSPECIFIED  # The spec says this value may be omitted


# Union of the two valid result types
Result = Union[Success, Error]


def InvalidParams(data: Any = UNSPECIFIED) -> Error:
    return Error(status.JSONRPC_INVALID_PARAMS_CODE, "Invalid params", data)


def MethodNotFound(data: Any) -> Error:
    return Error(status.JSONRPC_METHOD_NOT_FOUND_CODE, "Method not found", data)


def InternalError(data: Any) -> Error:
    return Error(status.JSONRPC_INTERNAL_ERROR_CODE, "Internal error", data)
