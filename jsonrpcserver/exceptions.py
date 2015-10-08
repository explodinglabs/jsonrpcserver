"""
exceptions.py

Specification: http://www.jsonrpc.org/specification#error_object

For the HTTP Status codes, see
http://jsonrpc.org/historical/json-rpc-over-http.html
"""

from . import status


class JsonRpcServerError(Exception):
    """Base class for the other exceptions"""

    def __init__(self, http_status, jsonrpc_status, message, data=None):
        """
        :param http_status: The HTTP error code. See
            http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.htmlstatus.py.
        :param jsonrpc_status_code: The JSON-RPC status code. See
            http://www.jsonrpc.org/specification#error_object
        :param message: The error message.
        :param data: Extra info (optional).
        """
        super(JsonRpcServerError, self).__init__(message)
        self.http_status = http_status
        self.jsonrpc_status = jsonrpc_status
        self.data = data


class ParseError(JsonRpcServerError):
    """
    An error occurred on the server while parsing the JSON string.

    No arguments are needed - there's no need for any further explanation.
    """

    def __init__(self):
        super(ParseError, self).__init__(
            status.JSONRPC_PARSE_ERROR_HTTP_CODE,
            status.JSONRPC_PARSE_ERROR_CODE, status.JSONRPC_PARSE_ERROR_TEXT)


class InvalidRequest(JsonRpcServerError):
    """
    The request is not a JSON-RPC object.

    Raised if the request fails the jsonschema validation.
    """

    def __init__(self, data=None):
        """
        :param data: Extra information (optional).
        """
        super(InvalidRequest, self).__init__(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, data)


class MethodNotFound(JsonRpcServerError):
    """
    The method does not exist / is not available.
    """

    def __init__(self, data=None):
        """
        :param data: Extra information (optional).
        """
        super(MethodNotFound, self).__init__(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_TEXT, data)


class InvalidParams(JsonRpcServerError):
    """
    Invalid method parameter(s).

    (The name of this error is incorrect in the specification, it should really
    be named "Invalid args".)

    Raised internally if the arguments don't match the method's parameters.
    Should also be raised in the application implementation itself, for example
    if arguments are invalid or a keyword argument is missing.
    """

    def __init__(self, data=None):
        """
        :param data: Extra information (optional).
        """
        super(InvalidParams, self).__init__(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT, data)


class ServerError(JsonRpcServerError):
    """
    There was an application specific error on the server-side.

    Can be raised by the application on discovering a problem such as a database
    connection failure.
    """

    def __init__(self, data=None):
        """
        :param data: Extra information (optional).
        """
        super(ServerError, self).__init__(
            status.JSONRPC_SERVER_ERROR_HTTP_CODE,
            status.JSONRPC_SERVER_ERROR_CODE, status.JSONRPC_SERVER_ERROR_TEXT,
            data)
