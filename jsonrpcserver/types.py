"""Types"""
from typing import Any, Callable, Dict, Iterator, Union

from .request import Request
from .response import Response

DeserializedRequest = Dict[str, Any]
DeserializedRequests = Union[DeserializedRequest, Iterator[DeserializedRequest]]
Requests = Union[Request, Iterator[Request]]
# Responses = Union[Response, Iterator[Response]]
Method = Callable[..., Any]
