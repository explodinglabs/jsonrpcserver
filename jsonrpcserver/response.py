"""
Response
********

The response objects returned by ``dispatch()``.
"""

import json
from collections import OrderedDict


def sort_response(response):
    """
    Sorts the keys in a JSON-RPC response object, returning a sorted
    OrderedDict. This has no effect other than making it nicer to read.

    Example::
        >>> json.dumps(sort_response({'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
        {"jsonrpc": "2.0", "result": 5, "id": 1}

    :param response: JSON-RPC response in dict format.
    :return: The same response, sorted in an ``OrderedDict``.
    """
    root_order = ['jsonrpc', 'result', 'error', 'id']
    error_order = ['code', 'message', 'data']
    if 'error' in response:
        response['error'] = OrderedDict(sorted(
            response['error'].items(), key=lambda k: error_order.index(k[0])))
    return OrderedDict(sorted(
        response.items(), key=lambda k: root_order.index(k[0])))


class _Response(object):
    """Parent of SuccessResponse and ErrorResponse"""

    def __init__(self, http_status, request_id):
        """
        :param http_status: The recommended HTTP status code to respond with,
                            if using HTTP for transport. Required even if not
                            using http.
        :param request_id: This member is REQUIRED. It MUST be the same as the
                           value of the id member in the Request Object. If
                           there was an error in detecting the id in the Request
                           object (e.g. Parse error/Invalid Request), it MUST be
                           Null.
        """
        #: Holds the HTTP status code to respond with (if using HTTP).
        self.http_status = http_status
        #: The 'id' part from the request to be sent back in the response.
        self.request_id = request_id

    @property
    def json(self):
        """Must be overridden in subclasses"""
        raise NotImplementedError()

    @property
    def json_debug(self):
        """Same as the json property, but with data added in error object."""
        return self.json

    @property
    def body(self):
        """The JSON-RPC response string."""
        return json.dumps(sort_response(self.json)) if self.json else ''

    @property
    def body_debug(self):
        """The JSON-RPC response string, with added ``data`` attribute."""
        return self.body


class SuccessResponse(_Response):
    """
    Success response object. Refer to the JSON-RPC `response object
    <http://www.jsonrpc.org/specification#response_object>`_ specification.

    :param request_id: Must be the same as the value as the id member in the
                       Request Object. If there was an error in detecting the id
                       in the Request object (e.g. Parse error/Invalid Request),
                       it MUST be Null.
    :param result: This member is REQUIRED on success. This member must not
                   exist if there was an error invoking the method.
    """

    def __init__(self, request_id, result):
        if result and not request_id:
            raise ValueError('Notifications cannot have a result payload')
        http_status = 200 if request_id else 204
        super(SuccessResponse, self).__init__(http_status, request_id)
        #: The payload from processing the request successfully.
        self.result = result

    @property
    def json(self):
        """The JSON-RPC response object in dict format."""
        if self.request_id:
            return {'jsonrpc': '2.0', 'result': self.result, 'id':
                    self.request_id}
        # else None


class ErrorResponse(_Response):
    """
    Error response object. Refer to the JSON-RPC `error object
    <http://www.jsonrpc.org/specification#error_object>`_ specification.

    :param http_status: The recommended HTTP status code to respond with, if
                        using HTTP for transport. Required even if not using
                        HTTP.
    :param request_id: Must be the same as the value as the id member in the
                       Request Object. If there was an error in detecting the id
                       in the Request object (e.g. Parse error/Invalid Request),
                       it MUST be Null.
    :param code: A Number that indicates the error type that occurred. This
                 MUST be an integer.
    :param message: A string providing a short description of the error, eg.
                    "Invalid params"
    :param data: A Primitive or Structured value that contains additional
                 information about the error. This may be omitted.
    """

    def __init__(self, http_status, request_id, code, message, data=None):
        super(ErrorResponse, self).__init__(http_status, request_id)
        #: Holds the JSON-RPC error code.
        self.code = code
        #: Holds the one-line message describing the error.
        self.message = message
        #: Holds the extra information about the error.
        self.data = data

    @property
    def json(self):
        """The JSON-RPC response object, in dictionary form."""
        return {'jsonrpc': '2.0', 'error': {'code': self.code, 'message': \
                self.message}, 'id': self.request_id}

    @property
    def json_debug(self):
        """The same as json property, but with extra data included."""
        r = self.json
        r['error']['data'] = self.data
        return r

    @property
    def body_debug(self):
        """The JSON-RPC response string, with added ``data`` attribute."""
        return json.dumps(sort_response(self.json_debug))
