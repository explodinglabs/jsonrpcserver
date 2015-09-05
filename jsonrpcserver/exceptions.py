"""exceptions.py

The error code numbers are defined by JSON-RPC.
See http://www.jsonrpc.org/specification#error_object

For the HTTP Status codes, see
http://jsonrpc.org/historical/json-rpc-over-http.html
"""

import json

from jsonrpcserver import rpc, status


class JsonRpcServerError(Exception):
    """Base class for the other exceptions"""

    def __init__(
            self, http_status_code, jsonrpc_status_code, message, data=None, \
            request_id=None):
        """
        :param http_status_code: The HTTP error code. See
            http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.htmlstatus.py.
        :param jsonrpc_status_code: The JSON-RPC status code. See
            http://www.jsonrpc.org/specification#error_object
        :param message: The error message.
        :param data: Extra info (optional).
        :param request_id: The id of the request, or None.
        """
        super(JsonRpcServerError, self).__init__(message)
        self.http_status_code = http_status_code
        self.jsonrpc_status_code = jsonrpc_status_code
        self.message = message
        self.data = data
        self.request_id = request_id

    def __str__(self):
        """Returns the error in a in JSON-RPC format response string"""
        return json.dumps(rpc.error(self.request_id, self.jsonrpc_status_code, \
            self.message, self.data), sort_keys=False)


class ParseError(JsonRpcServerError):
    """Raised when the JSON cannot be parsed.

    From the specs: 'Invalid JSON was received by the server. An error occurred
    on the server while parsing the JSON string.'

    No arguments are needed - there's no need for any further explanation, and
    we can't get the request_id because the request was not parsed.
    """

    def __init__(self):
        super(ParseError, self).__init__(
            status.JSONRPC_PARSE_ERROR_HTTP_CODE, \
            status.JSONRPC_PARSE_ERROR_CODE, \
            status.JSONRPC_PARSE_ERROR_TEXT)


class InvalidRequest(JsonRpcServerError):
    """The request is not a JSON-RPC object.

    From the specs: 'The JSON sent is not a valid Request object.'
    """

    def __init__(self, data=None, request_id=None):
        """
        :param data: Extra information (optional).
        :param request_id: The id of the request, or None.
        """
        super(InvalidRequest, self).__init__(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE, \
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, data, request_id)


class MethodNotFound(JsonRpcServerError):
    """The requested method does not exist.

    From the specs: 'The method does not exist / is not available.'
    """

    def __init__(self, data=None, request_id=None):
        """
        :param data: Extra information (optional).
        :param request_id: The id of the request, or None.
        """
        super(MethodNotFound, self).__init__(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE, \
            status.JSONRPC_METHOD_NOT_FOUND_CODE, \
            status.JSONRPC_METHOD_NOT_FOUND_TEXT, data, request_id)


class InvalidParams(JsonRpcServerError):
    """The arguments were incorrect.

    From the specs: 'Invalid method parameter(s).' Note the name of this error
    is incorrect in the specs, it should really be named "Invalid arguments".

    Raised internally if the arguments don't match the method's required
    arguments. It should also be raised in the application implementation
    itself, for example if arguments are invalid or a keyword argument is
    missing.
    """

    def __init__(self, data=None, request_id=None):
        """
        :param data: Extra information (optional).
        :param request_id: The id of the request, or None.
        """
        super(InvalidParams, self).__init__(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE, \
            status.JSONRPC_INVALID_PARAMS_CODE, \
            status.JSONRPC_INVALID_PARAMS_TEXT, data, request_id)


class ServerError(JsonRpcServerError):
    """There was an application specific error on the server-side.

    Can be raised by the application on discovering a problem such as a database
    connection failure.
    """

    def __init__(self, data=None, request_id=None):
        """
        :param data: Extra information (optional).
        :param request_id: The id of the request, or None.
        """
        super(ServerError, self).__init__(
            status.JSONRPC_SERVER_ERROR_HTTP_CODE, \
            status.JSONRPC_SERVER_ERROR_CODE, \
            status.JSONRPC_SERVER_ERROR_TEXT, data, request_id)
