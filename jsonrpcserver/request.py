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


def is_notification(request: Request) -> bool:
    """
    Returns:
        True if the request is a JSON-RPC Notification (ie. No id attribute is
        included). False if it doesn't, meaning it's a JSON-RPC "Request".
    """
    return request.id is NOID
