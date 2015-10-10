"""
Exceptions
**********

Errors are defined at the JSON-RPC `specification
<http://www.jsonrpc.org/specification#error_object>`_. HTTP status codes chosen
for each error were taken from `this document
<http://jsonrpc.org/historical/json-rpc-over-http.html>`_.
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
    are needed - there's no need for any further explanation.
    """

    def __init__(self):
        super(ParseError, self).__init__(
            status.JSONRPC_PARSE_ERROR_HTTP_CODE,
            status.JSONRPC_PARSE_ERROR_CODE, status.JSONRPC_PARSE_ERROR_TEXT)


class InvalidRequest(JsonRpcServerError):
    """
    The request is not a JSON-RPC object. Raised if the request fails the
    jsonschema validation.

    :param data: Extra information (optional).
    """

    def __init__(self, data=None):
        super(InvalidRequest, self).__init__(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, data)


class MethodNotFound(JsonRpcServerError):
    """
    The method does not exist/is not available.

    :param data: Extra information (optional).
    """

    def __init__(self, data=None):
        super(MethodNotFound, self).__init__(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_CODE,
            status.JSONRPC_METHOD_NOT_FOUND_TEXT, data)


class InvalidParams(JsonRpcServerError):
    """
    Invalid method parameter(s). Raised internally if the arguments don't match
    the method's parameters.  Should also be raised in the application
    implementation itself, for example if arguments are invalid or a keyword
    argument is missing.

    :param data: Extra information (optional).
    """

    def __init__(self, data=None):
        super(InvalidParams, self).__init__(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT, data)


class ServerError(JsonRpcServerError):
    """
    There was an application specific error on the server-side. Can be raised
    by the application on discovering a problem such as a database connection
    failure.

    :param data: Extra information (optional).
    """

    def __init__(self, data=None):
        super(ServerError, self).__init__(
            status.JSONRPC_SERVER_ERROR_HTTP_CODE,
            status.JSONRPC_SERVER_ERROR_CODE, status.JSONRPC_SERVER_ERROR_TEXT,
            data)
