from typing import Any, Awaitable, Callable, Dict, Optional, cast

from returns.result import Result

from .result import ErrorResult, SuccessResult

Method = Callable[..., Awaitable[Result[SuccessResult, ErrorResult]]]
Methods = Dict[str, Method]
global_methods: Methods = dict()


def method(
    f: Optional[Method] = None, name: Optional[str] = None
) -> Callable[..., Awaitable[Any]]:
    """A decorator to add a function into jsonrpcserver's internal global_methods dict.
    The global_methods dict will be used by default unless a methods argument is passed
    to `dispatch`.

    Functions can be renamed by passing a name argument:

        @method(name=bar)
        def foo():
            ...
    """

    def decorator(func: Method) -> Method:
        nonlocal name
        global_methods[name or func.__name__] = func
        return func

    return decorator(f) if callable(f) else cast(Method, decorator)
