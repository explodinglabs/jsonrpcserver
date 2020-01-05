"""
The "methods" object holds the list of functions that can be called by remote calls.

Add as many methods as needed.

Methods can take either positional or named arguments (but not both, this is a
limitation of JSON-RPC).
"""
from typing import Any, Callable, Optional

from inspect import signature

from .exceptions import MethodNotFoundError, InvalidParamsError

Method = Callable[..., Any]


def validate_args(func: Method, *args: Any, **kwargs: Any) -> Method:
    """
    Check if the request's arguments match a function's signature.

    Raises InvalidParamsError if arguments cannot be passed to a function.

    Args:
        func: The function to check.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        The same function passed in.

    Raises:
        InvalidParamsError: If the arguments cannot be passed to the function.
    """
    try:
        signature(func).bind(*args, **kwargs)
    except TypeError as exc:
        raise InvalidParamsError from exc
    return func


def validate(method: Callable) -> Callable:
    assert callable(method)
    return method


class Methods:
    """Holds a list of methods that can be called by a JSON-RPC request."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.items = {}  # type: dict
        self.add(*args, **kwargs)

    def add(self, *args: Any, **kwargs: Any) -> Optional[Callable]:
        """
        Register a function to the list.

        Args:
            *args: Set/Sequence of positional arguments.
            **kwargs: Mapping of named arguments.

        Raises:
            AttributeError: Raised if the method being added has no name. (i.e. it has
                no `__name__` property, and no `name` argument was given.)

        Examples:
            methods = Methods()
            @methods.add
            def subtract(minuend, subtrahend):
                return minuend - subtrahend
        """
        self.items = {
            **self.items,
            # Methods passed as positional args need a __name__ attribute, raises
            # AttributeError otherwise.
            **{m.__name__: validate(m) for m in args},
            **{k: validate(v) for k, v in kwargs.items()},
        }
        if len(args):
            return args[0]  # for the decorator to work
        return None


def lookup(methods: Methods, method_name: str) -> Method:
    """
    Lookup a method.

    Args:
        methods: Methods object
        method_name: Method name to look up

    Returns:
        The callable method.

    Raises:
        MethodNotFoundError if method_name is not found.
    """
    try:
        return methods.items[method_name]
    except KeyError as exc:
        raise MethodNotFoundError(method_name) from exc


# A default Methods object which can be used, or user can create their own.
global_methods = Methods()


def add(*args: Any, **kwargs: Any) -> Optional[Callable]:
    return global_methods.add(*args, **kwargs)
