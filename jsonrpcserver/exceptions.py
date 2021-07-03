"""
An exception can be raised from inside a method to return an error response.

This is an alternative to returning a Result from the method.

See https://github.com/bcb/jsonrpcserver/discussions/158
"""


class JsonRpcError(Exception):
    def __init__(self, code: int, message: str, data: str):
        self.code, self.message, self.data = (code, message, data)
