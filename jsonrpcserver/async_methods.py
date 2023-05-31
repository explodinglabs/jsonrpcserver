"""Async methods"""
from typing import Any, Awaitable, Callable, Dict, Optional, cast

from returns.result import Result

from .result import ErrorResult, SuccessResult

Method = Callable[..., Awaitable[Result[SuccessResult, ErrorResult]]]
Methods = Dict[str, Method]
global_methods: Methods = {}


def method(
    func: Optional[Method] = None, name: Optional[str] = None
) -> Callable[..., Awaitable[Any]]:
    """A decorator to add a function into jsonrpcserver's internal global_methods dict.
    The global_methods dict will be used by default unless a methods argument is passed
    to `dispatch`.

    Functions can be renamed by passing a name argument:

        @method(name=bar)
        def foo():
            ...
    """

    def decorator(func_: Method) -> Method:
        nonlocal name
        global_methods[name or func_.__name__] = func_
        return func_

    return decorator(func) if callable(func) else cast(Method, decorator)
