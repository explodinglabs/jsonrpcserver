from functools import reduce
from typing import Any, Callable


identity = lambda x: x


def compose(*funcs: Callable) -> Callable:
    return lambda x: reduce(lambda acc, f: f(acc), reversed(funcs), x)


def make_list(x: Any) -> list:
    return [x] if not isinstance(x, list) else x
