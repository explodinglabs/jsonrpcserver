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
            self, http_status_code, jsonrpc_status_code, text, data=None, \
            request_id=None):

        super().__init__(text)
        self.http_status_code = http_status_code
        self.jsonrpc_status_code = jsonrpc_status_code
        self.text = text
        self.data = data
        self.request_id = request_id

    def __str__(self):
        """Returns the error in a in JSON-RPC format response string"""

        return json.dumps(
            rpc.error(self.request_id, self.jsonrpc_status_code, self.text, \
                self.data), sort_keys=False)

class ParseError(JsonRpcServerError):
    """From the specs: 'Invalid JSON was received by the server. An error
    occurred on the server while parsing the JSON text.'

    ParseError is raised when the request is jumbled and cannot be parsed.

    No arguments should be passed - there's no need for any further explanation,
    and we can't give a request_id back, because the request was simply not
    parsed.
    """

    def __init__(self):
        super().__init__(
            status.JSONRPC_PARSE_ERROR_HTTP_CODE, \
            status.JSONRPC_PARSE_ERROR_CODE, \
            status.JSONRPC_PARSE_ERROR_TEXT)

class InvalidRequest(JsonRpcServerError):
    """From the specs: 'The JSON sent is not a valid Request object.'

    InvalidRequest is raised in two situations:

    1. When the request doesn't validate against json-rpc schema. In this case
    it gives the reason as a string, chosen by the jsonschema package as the
    best match.

    2. When flask gets a client error such as 404. In this case the reason is
    given as the HTTP status code name, such as "File not found".

    string @reason: The reason the request is invalid, placed in the data field.
    """

    def __init__(self, reason, request_id=None):
        super().__init__(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE, \
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, reason, request_id)

class MethodNotFound(JsonRpcServerError):
    """From the specs: 'The method does not exist / is not available.'

    MethodNotFound is raised when the message was parsed OK but the requested
    method doesn't exist.

    string @method_name: To be returned in the data field.
    """

    def __init__(self, method_name, request_id=None):
        super().__init__(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE, \
            status.JSONRPC_METHOD_NOT_FOUND_CODE, \
            status.JSONRPC_METHOD_NOT_FOUND_TEXT, method_name, request_id)

class InvalidParams(JsonRpcServerError):
    """From the specs: 'Invalid method parameter(s).'

    InvalidParams is raised by dispatch() method if a TypeError is caught when
    trying to dispatch to the requested method.

    It should also be raised by the application implementation itself, if params
    are required but were not given or not valid.

    The "params" param should be either a list of the invalid param names, or a
    dict with further information about each.
    """

    def __init__(self, params, request_id=None):
        super().__init__(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE, \
            status.JSONRPC_INVALID_PARAMS_CODE, \
            status.JSONRPC_INVALID_PARAMS_TEXT, params, request_id)

class ServerError(JsonRpcServerError):
    """From the specs: 'Internal JSON-RPC error.'

    ServerError is a generic response when there's an error on the server end.
    Apps should subclass it.
    """

    def __init__(
            self, message=status.JSONRPC_SERVER_ERROR_TEXT, \
            data=None, request_id=None):
        super().__init__(
            status.JSONRPC_SERVER_ERROR_HTTP_CODE, \
            status.JSONRPC_SERVER_ERROR_CODE, \
            message, data, request_id)
