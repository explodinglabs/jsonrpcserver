"""Types"""
from typing import Any, Callable, Dict, Iterable, Union

from .request import Request
from .response import Response

DeserializedRequest = Dict[str, Any]
DeserializedRequests = Union[DeserializedRequest, Iterable[DeserializedRequest]]
Requests = Union[Request, Iterable[Request]]
Method = Callable[..., Any]
