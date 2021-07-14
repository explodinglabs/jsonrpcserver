"""
Request class.

Represents a JSON-RPC request object.
"""
from typing import Any, NamedTuple, Union


class NoId:
    def __repr__(self) -> str:
        return "<no id>"


NOID = NoId()


Request = NamedTuple(
    "Request",
    [
        ("method", str),
        ("params", Union[list, dict]),
        ("id", Any),  # Use NOID for a Notification.
    ],
)
