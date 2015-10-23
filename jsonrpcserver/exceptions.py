"""
Exceptions
**********

These exceptions are raised internally by the library, but can also raised by
applications wanting to return an error to the client.
"""

from jsonrpcserver import status


class JsonRpcServerError(Exception):
    """
    Base class for the other exceptions.

    :param http_status: The HTTP status code.
    :param jsonrpc_status_code: The JSON-RPC status code.
    :param message: The one-line error message.
    :param data: Extra info (optional).
    """

    def __init__(self, http_status, jsonrpc_status, message, data=None):
        super(JsonRpcServerError, self).__init__(message)
        #: Holds the http status code.
        self.http_status = http_status
        #: Holds the jsonrpc status code.
        self.jsonrpc_status = jsonrpc_status
        #: Holds the extra information related to the error.
        self.data = data


class ParseError(JsonRpcServerError):
    """
    An error occurred on the server while parsing the JSON string. No arguments
    are needed because there's no need for any further explanation.
    """

    def __init__(self):
        super(ParseError, self).__init__(
            status.JSONRPC_PARSE_ERROR_HTTP_CODE,
            status.JSONRPC_PARSE_ERROR_CODE, status.JSONRPC_PARSE_ERROR_TEXT)


class InvalidRequest(JsonRpcServerError):
    """
    The request is not a JSON-RPC object. Raised if the request fails the
    jsonschema validation.

    :param data: Extra information about the error that occurred (optional).
    """

    def __init__(self, data=None):
        super(InvalidRequest, self).__init__(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, data)


class MethodNotFound(JsonRpcServerError):
    """
    The method does not exist/is not available.

    :param data: Extra information about the error that occurred (optional).
    """

    def __init__(self, data=None):
        super(MethodNotFound, self).__init__(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_TEXT, data)


class InvalidParams(JsonRpcServerError):
    """
    Raised when invalid arguments are passed to a method. e.g. if a required
    keyword argument is missing.

    :param data: Extra information about the error that occurred (optional).
    """

    def __init__(self, data=None):
        super(InvalidParams, self).__init__(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT, data)


class ServerError(JsonRpcServerError):
    """
    Raised when there's an application specific error on the server-side.

    :param data: Extra information about the error that occurred (optional).
    """

    def __init__(self, data=None):
        super(ServerError, self).__init__(
            status.JSONRPC_SERVER_ERROR_HTTP_CODE,
            status.JSONRPC_SERVER_ERROR_CODE, status.JSONRPC_SERVER_ERROR_TEXT,
            data)
