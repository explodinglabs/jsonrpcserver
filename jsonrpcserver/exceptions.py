"""
Exceptions
**********

These exceptions are raised to trigger returning an error to the client.

Attributes can be monkey patched to configure error responses, for example::

    from jsonrpcserver.exceptions import InvalidParams
    InvalidParams.message = 'Invalid arguments'
    InvalidParams.http_status = 406
"""

from jsonrpcserver import status

class JsonRpcServerError(Exception):
    """Base class for the other exceptions.

    :param data: Extra info (optional).
    """

    message = None

    def __init__(self, data=None):
        super(JsonRpcServerError, self).__init__(self.message)
        #: Holds the extra information related to the error.
        self.data = data


class ParseError(JsonRpcServerError):
    """The request is not a valid JSON object."""

    #: Error code
    code = -32700
    #: The message
    message = 'Parse error'
    #: HTTP status
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self):
        super(ParseError, self).__init__()


class InvalidRequest(JsonRpcServerError):
    """The request is not a valid JSON-RPC object.

    :param data: Extra information about the error that occurred (optional).
    """

    #: Error code
    code = -32600
    #: The message
    message = 'Invalid request'
    #: HTTP status
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidRequest, self).__init__(data)


class MethodNotFound(JsonRpcServerError):
    """The method does not exist/is not available.

    :param data: Extra information about the error that occurred (optional).
    """

    #: Error code
    code = -32601
    #: The message
    message = 'Method not found'
    #: HTTP status
    http_status = status.HTTP_NOT_FOUND

    def __init__(self, data=None):
        super(MethodNotFound, self).__init__(data)


class InvalidParams(JsonRpcServerError):
    """Raised when invalid arguments are passed to a method, e.g. if a required
    keyword argument is missing.

    :param data: Extra information about the error that occurred (optional).
    """

    #: Error code
    code = -32602
    #: The message
    message = 'Invalid params'
    #: HTTP status
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidParams, self).__init__(data)


class ServerError(JsonRpcServerError):
    """Raised when there's an application specific error on the server-side.

    :param data: Extra information about the error that occurred (optional).
    """

    #: Error code
    code = -32000
    #: The message
    message = 'Server error'
    #: HTTP status
    http_status = status.HTTP_INTERNAL_ERROR

    def __init__(self, data=None):
        super(ServerError, self).__init__(data)
