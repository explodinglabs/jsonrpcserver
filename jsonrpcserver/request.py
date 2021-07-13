"""
Request class.

Represents a JSON-RPC request object.
"""
from typing import Any, NamedTuple, Union

NOID = object()


Request = NamedTuple(
    "Request",
    [
        ("method", str),
        ("params", Union[list, dict]),
        ("id", Any),  # Use NOID for a Notification.
    ],
)
