"""The methods dictionary holds the list of functions that can be called by remote
calls. It's a mapping of function names to functions.

Methods can take either positional or named arguments, but not both - this is a
limitation of JSON-RPC.
"""
from typing import Callable, Dict, Optional

from .result import Result

Method = Callable[..., Result]
Methods = Dict[str, Method]

# A default Methods object which can be used, or user can create their own.
global_methods = dict()


def method(f: Optional[Method] = None, name: Optional[str] = None) -> function:
    def decorator(func: Method) -> Method:
        nonlocal name
        global global_methods
        global_methods[name or func.__name__] = func
        return func

    return decorator(f) if callable(f) else decorator
