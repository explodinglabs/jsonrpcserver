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
from typing import Any, NamedTuple

from oslash.either import Either  # type: ignore

from .codes import ERROR_INVALID_PARAMS, ERROR_METHOD_NOT_FOUND, ERROR_INTERNAL_ERROR

# This is used to indicate when a value isn't present. We use this instead of
# None, because None is a valid JSON-serializable type.
UNSPECIFIED = object()


class SuccessResult(NamedTuple):
    result: Any

    def __repr__(self) -> str:
        return f"SuccessResult({self.result!r})"


class ErrorResult(NamedTuple):
    code: int
    message: str
    data: Any = UNSPECIFIED  # The spec says this value may be omitted

    def __repr__(self) -> str:
        return f"ErrorResult(code={self.code!r}, message={self.message!r}, data={self.data!r}"


# Union of the two valid result types
Result = Either[SuccessResult, ErrorResult]


# Helpers


def MethodNotFoundResult(data: Any) -> ErrorResult:
    return ErrorResult(ERROR_METHOD_NOT_FOUND, "Method not found", data)


def InternalErrorResult(data: Any) -> ErrorResult:
    return ErrorResult(ERROR_INTERNAL_ERROR, "Internal error", data)


def InvalidParamsResult(data: Any = UNSPECIFIED) -> ErrorResult:
    return ErrorResult(ERROR_INVALID_PARAMS, "Invalid params", data)
