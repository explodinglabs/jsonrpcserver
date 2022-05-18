"""Result data types - the results of calling a method.

Results are the JSON-RPC response objects
(https://www.jsonrpc.org/specification#response_object), minus the "jsonrpc" and "id"
parts - the library takes care of these parts for you.

The public functions are Success, Error and InvalidParams.
"""
from typing import Any, NamedTuple

from returns.result import Failure, Result, Success

from .codes import ERROR_INVALID_PARAMS, ERROR_METHOD_NOT_FOUND, ERROR_INTERNAL_ERROR
from .sentinels import NODATA


class SuccessResult(NamedTuple):
    result: Any = None

    def __repr__(self) -> str:
        return f"SuccessResult({self.result!r})"


class ErrorResult(NamedTuple):
    code: int
    message: str
    data: Any = NODATA  # The spec says this value may be omitted

    def __repr__(self) -> str:
        return f"ErrorResult(code={self.code!r}, message={self.message!r}, data={self.data!r})"


# Helpers


def MethodNotFoundResult(data: Any) -> ErrorResult:
    return ErrorResult(ERROR_METHOD_NOT_FOUND, "Method not found", data)


def InternalErrorResult(data: Any) -> ErrorResult:
    return ErrorResult(ERROR_INTERNAL_ERROR, "Internal error", data)


def InvalidParamsResult(data: Any = NODATA) -> ErrorResult:
    return ErrorResult(ERROR_INVALID_PARAMS, "Invalid params", data)


# Helpers (the public functions)


def Ok(*args: Any, **kwargs: Any) -> Result[SuccessResult, ErrorResult]:
    return Success(SuccessResult(*args, **kwargs))


def Error(*args: Any, **kwargs: Any) -> Result[SuccessResult, ErrorResult]:
    return Failure(ErrorResult(*args, **kwargs))


def InvalidParams(*args: Any, **kwargs: Any) -> Result[SuccessResult, ErrorResult]:
    """InvalidParams is a shortcut to save you from having to pass the Invalid Params
    JSON-RPC code to Error.
    """
    return Failure(InvalidParamsResult(*args, **kwargs))
