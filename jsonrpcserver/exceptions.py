"""A JsonRpcError exception can be raised from inside a method, as an alternative way to
return an error response. See https://github.com/bcb/jsonrpcserver/discussions/158
"""
from typing import Any
from .sentinels import NODATA


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: Any = NODATA):
        self.code, self.message, self.data = (code, message, data)
