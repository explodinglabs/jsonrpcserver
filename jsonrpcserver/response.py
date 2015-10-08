"""
response.py

The success and error response objects as defined in the JSON-RPC spec.

Note the 'id' is required in the response, even if null, for both success and
error.

Specification: http://www.jsonrpc.org/specification#response_object
"""

import json
from collections import OrderedDict


def sort_response(response):
    """
    Sorts the keys in a JSON-RPC response, returning a sorted OrderedDict. This
    has no effect other than making it nicer to read.

    Example::
        >>> json.dumps(sort_response({'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
        {"jsonrpc": "2.0", "result": 5, "id": 1}

    :param response: JSON-RPC response in dict format.
    :return: The same response, nicely sorted.
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
        Specification: http://www.jsonrpc.org/specification#response_object

        :param http_status: Used to respond if using http for transport.
            Required even if not using http.
        :param request_id: This member is REQUIRED. It MUST be the same as the
        value of the id member in the Request Object. If there was an error in
        detecting the id in the Request object (e.g. Parse error/Invalid
        Request), it MUST be Null.
        """
        self.http_status = http_status
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
        """
        The string version of the json property.
        """
        return json.dumps(sort_response(self.json)) if self.json else ''

    @property
    def body_debug(self):
        """Same as the body property, but with data added in error object."""
        return self.body


class SuccessResponse(_Response):
    """
    The JSON-RPC Response object.
    Specification: http://www.jsonrpc.org/specification#response_object
    """

    def __init__(self, request_id, result):
        """
        :param request_id: See description in parent class.
        :param result: This member is REQUIRED on success. This member must not
        exist if there was an error invoking the method.
        """
        if result and not request_id:
            raise ValueError('Notification response cannot have no result')
        http_status = 200 if request_id else 204
        super(SuccessResponse, self).__init__(http_status, request_id)
        self.result = result

    @property
    def json(self):
        if self.request_id:
            return {'jsonrpc': '2.0', 'result': self.result, 'id':
                    self.request_id}
        # else None


class ErrorResponse(_Response):
    """
    The JSON-RPC Error object.
    Specification: http://www.jsonrpc.org/specification#error_object
    """

    def __init__(self, http_status, request_id, code, message, data=None):
        """
        :param http_status: See description in parent class.
        :param request_id: See description in parent class.
        :param code: A Number that indicates the error type that occurred. This
        MUST be an integer.
        :param message: A string providing a short description of the error, eg.
        "Invalid params"
        :param data: A Primitive or Structured balue that contains additional
        information about the error. This may be omitted.
        :return: The response dict.
        """
        super(ErrorResponse, self).__init__(http_status, request_id)
        self.code = code
        self.message = message
        self.data = data

    @property
    def json(self):
        return {'jsonrpc': '2.0', 'error': {'code': self.code, 'message': \
                self.message}, 'id': self.request_id}

    @property
    def json_debug(self):
        """Return the same as json method, but with error/data included"""
        r = self.json
        r['error']['data'] = self.data
        return r

    @property
    def body_debug(self):
        """
        The string version of the json property (which returns a dict).
        """
        return json.dumps(sort_response(self.json_debug))
