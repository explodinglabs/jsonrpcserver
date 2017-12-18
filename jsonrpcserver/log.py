"""Logging"""
import logging


def _configure_logger(logger, fmt):
    """
    Set up a logger, if no handler has been configured for it.

    Used by log_ below.
    """
    if logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
    if not logging.root.handlers and not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(handler)


def log_(logger, level, message, *args, **kwargs):
    """
    Log a message.

    The trailing underscore is to avoid clashing with python's builtin log
    function
    """
    fmt = kwargs.pop('fmt', '%(message)s')
    _configure_logger(logger, fmt)
    getattr(logger, level)(message, *args, **kwargs)
