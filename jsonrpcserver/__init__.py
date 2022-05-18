"""Use __all__ so mypy considers these re-exported."""
__all__ = [
    "Error",
    "InvalidParams",
    "JsonRpcError",
    "Ok",
    "Result",
    "Success",
    "async_dispatch",
    "async_dispatch_to_response",
    "async_dispatch_to_serializable",
    "async_method",
    "dispatch",
    "dispatch_to_response",
    "dispatch_to_serializable",
    "method",
    "serve",
]

from returns.result import Result as R

from .async_main import (
    dispatch as async_dispatch,
    dispatch_to_response as async_dispatch_to_response,
    dispatch_to_serializable as async_dispatch_to_serializable,
)
from .async_methods import method as async_method
from .exceptions import JsonRpcError
from .main import dispatch, dispatch_to_response, dispatch_to_serializable
from .methods import method
from .result import Error, InvalidParams, Ok, SuccessResult, ErrorResult
from .server import serve as serve

# For backward compatibility
Result = R[SuccessResult, ErrorResult]
Success = Ok
