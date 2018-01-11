"""Logging"""
import logging


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


def log(logger, level, message, *args, **kwargs):
    """
    Log a message.

    The trailing underscore is to avoid clashing with python's builtin log
    function
    """
    fmt = kwargs.pop('fmt', '%(message)s')
    configure_logger(logger, fmt)
    getattr(logger, level)(message, *args, **kwargs)
