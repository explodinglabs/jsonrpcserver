"""Exceptions raised by jsonrpcserver."""

from jsonrpcserver import status

class JsonRpcServerError(Exception):
    """Base class for the other exceptions.

    :param data: Extra info (optional).
    """
    message = None

    def __init__(self, data=None):
        super(JsonRpcServerError, self).__init__(self.message)
        # Holds extra information related to the error.
        self.data = data


class ParseError(JsonRpcServerError):
    """Raised when the request is not a valid JSON object."""
    code = -32700
    message = 'Parse error'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self):
        super(ParseError, self).__init__()


class InvalidRequest(JsonRpcServerError):
    """Raised when the request is not a valid JSON-RPC object.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32600
    message = 'Invalid Request'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidRequest, self).__init__(data)


class MethodNotFound(JsonRpcServerError):
    """Raised when the method does not exist/is not available.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32601
    message = 'Method not found'
    http_status = status.HTTP_NOT_FOUND

    def __init__(self, data=None):
        super(MethodNotFound, self).__init__(data)


class InvalidParams(JsonRpcServerError):
    """Raised when invalid arguments are passed to a method, e.g. if a required
    keyword argument is missing.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32602
    message = 'Invalid params'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidParams, self).__init__(data)


class ServerError(JsonRpcServerError):
    """Raised when there's an application-specific error on the server side.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32000
    message = 'Server error'
    http_status = status.HTTP_INTERNAL_ERROR

    def __init__(self, data=None):
        super(ServerError, self).__init__(data)
