"""Logging"""
import logging
import json


def configure_logger(logger, fmt):
    """
    Set up a logger, if no handler has been configured for it.

    Used by the log function below.
    """
    if logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    if not logging.root.handlers and not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(handler)


def _trim_string(message):
    longest_string = 30

    if len(message) > longest_string:
        prefix_len = int(longest_string / 3)
        suffix_len = prefix_len
        return message[:prefix_len] + "..." + message[-suffix_len:]

    return message


def _trim_values(message_obj):
    result = {}
    longest_list = 30
    for k, val in message_obj.items():
        if isinstance(val, str):
            result[k] = _trim_string(val)
        elif isinstance(val, list) and len(val) > longest_list:
            prefix_len = int(longest_list / 3)
            suffix_len = prefix_len
            result[k] = val[:prefix_len] + ["..."] + val[-suffix_len:]
        elif isinstance(val, dict):
            result[k] = _trim_values(val)
        else:
            result[k] = val
    return result


def trim_message(message):
    try:
        message_obj = json.loads(message)
        return json.dumps(_trim_values(message_obj))
    except ValueError:
        return _trim_string(str(message))


def log(logger, level, message, *args, **kwargs):
    """
    Log a message.
    """
    fmt = kwargs.pop("fmt", "%(message)s")
    trim = kwargs.pop("trim", False)
    if trim:
        message = trim_message(message)
    configure_logger(logger, fmt)
    logger.log(level, message, *args, **kwargs)
