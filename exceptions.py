"""exceptions.py

The error code numbers are defined by JSON-RPC.
See http://www.jsonrpc.org/specification#error_object"""

import json

from . import rpc

class RPCHandlerException(Exception):
    """Base class for the other rpchandler exceptions"""

    def __init__(self, code, message, **kwargs):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = None
        self.request_id = None

        if 'data' in kwargs:
            self.data = kwargs['data']

        if 'request_id' in kwargs:
            self.request_id = kwargs['request_id']

    def __str__(self):
        """Returns the error in a in JSON-RPC format response string"""

        return json.dumps(
            rpc.error(self.request_id, self.code, self.message, self.data), \
            sort_keys=False)

class ParseError(RPCHandlerException):
    """Could not parse the request string. Invalid JSON."""

    def __init__(self):
        super().__init__(-32700, 'Parse error')

class InvalidRequest(RPCHandlerException):
    """The JSON sent didn't validate against the JSON-RPC request schema."""

    def __init__(self, validation_errors, **kwargs):
        super().__init__(
            -32600, 'Invalid request', data=validation_errors, **kwargs)

class MethodNotFound(RPCHandlerException):
    """The method does not exist/is not available."""

    def __init__(self, **kwargs):
        super().__init__(-32601, 'Method not found', **kwargs)

class InvalidParams(RPCHandlerException):
    """Invalid method parameter(s)."""

    def __init__(self, message, **kwargs):
        super().__init__(-32602, message, **kwargs)
