"""Logging"""
import json
import logging
from typing import Any, Dict, List, Optional, Union, cast


def _trim_string(message: str) -> str:
    longest_string = 30

    if len(message) > longest_string:
        prefix_len = int(longest_string / 3)
        suffix_len = prefix_len
        return message[:prefix_len] + "..." + message[-suffix_len:]

    return message


def _trim_dict(message_obj: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    longest_list = 30
    for k, val in message_obj.items():
        if isinstance(val, str):
            result[k] = _trim_string(val)
        elif isinstance(val, list) and len(val) > longest_list:
            prefix_len = int(longest_list / 3)
            suffix_len = prefix_len
            result[k] = cast(str, val[:prefix_len] + ["..."] + val[-suffix_len:])
        elif isinstance(val, dict):
            result[k] = cast(str, _trim_values(val))
        else:
            result[k] = val
    return result


def _trim_values(message_obj: Union[Dict, List]) -> Union[Dict, List]:
    # Batch?
    if isinstance(message_obj, list):
        return [_trim_dict(i) for i in message_obj]
    else:
        return _trim_dict(message_obj)


def _trim_message(message: str) -> str:
    # Attempt to deserialize
    try:
        message_obj = json.loads(message)
    except ValueError:
        # Could not be deserialized, trim the string anyway.
        return _trim_string(str(message))
    else:
        return json.dumps(_trim_values(message_obj))


def log_(
    message: str,
    logger: logging.Logger,
    level: str = "info",
    extra: Optional[Dict] = None,
    trim: bool = False,
) -> None:
    """
    Log a request or response

    Args:
        message: JSON-RPC request or response string.
        level: Log level.
        extra: More details to include in the log entry.
        trim: Abbreviate log messages.
    """
    if extra is None:
        extra = {}
    # Clean up the message for logging
    if message:
        message = message.replace("\n", "").replace("  ", " ").replace("{ ", "{")
    if trim:
        message = _trim_message(message)
    # Log.
    getattr(logger, level)(message, extra=extra)
