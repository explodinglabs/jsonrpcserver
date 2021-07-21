from functools import reduce
from typing import Any, Callable, List


identity = lambda x: x


def compose(*funcs: Callable[..., Any]) -> Callable[..., Any]:
    return lambda x: reduce(lambda acc, f: f(acc), reversed(funcs), x)


def make_list(x: Any) -> List[Any]:
    return [x] if not isinstance(x, list) else x
