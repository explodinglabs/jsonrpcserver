"""Jsonrpcserver"""
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
from .result import Error, ErrorResult, InvalidParams, Ok, SuccessResult
from .server import serve

Success = Ok  # For backward compatibility - version 5 used Success instead of Ok
Result = R[SuccessResult, ErrorResult]


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
