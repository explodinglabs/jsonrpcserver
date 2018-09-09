"""Types"""
from typing import Any, Dict, List, Union
from .response import Response


Request = Dict[str, Any]
Requests = Union[Request, List[Request]]
Responses = Union[Response, List[Response]]
