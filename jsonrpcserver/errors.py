"""Exceptions"""
from typing import Any

from .response import UNSPECIFIED
from . import status

class MethodNotFoundError(KeyError):
    """ Method lookup failed """
    pass

class ApiError(RuntimeError):
    """ A method responds with a custom error """

    def __init__(
        self,
        message: str,
        code: int = status.JSONRPC_SERVER_ERROR_CODE,
        data: Any = UNSPECIFIED,
        ):
        """
        Args:
            message: A string providing a short description of the error, eg.  "Invalid
                params".
            code: A Number that indicates the error type that occurred. This MUST be an
                integer.
            data: A Primitive or Structured value that contains additional information
                about the error. This may be omitted.
        """
        super().__init__(message)
        self.code = code
        self.data = data
