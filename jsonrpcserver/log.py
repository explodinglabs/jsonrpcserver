"""Logging"""

import logging

def _configure_logger(logger, fmt):
    """Set up a logger, if no handler has been configured for it"""
    if not logging.root.handlers and logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=fmt))
        logger.addHandler(handler)


def _log(logger, level, message, *args, **kwargs):
    """Configure before logging"""
    fmt = kwargs.pop('fmt', '%(message)s')
    _configure_logger(logger, fmt)
    getattr(logger, level)(message, *args, **kwargs)
