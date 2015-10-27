"""
Response
********

The objects returned by `dispatch()`_.

.. _dispatch(): #dispatcher.dispatch
"""

import json
from collections import OrderedDict
from jsonrpcserver import status

def _sort_response(response):
    """Sort the keys in a JSON-RPC response object.

    This has no effect other than making it nicer to read.

    Example::

        >>> json.dumps(_sort_response({'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
        {"jsonrpc": "2.0", "result": 5, "id": 1}

    :param response: JSON-RPC response, in dictionary form.
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
    """Parent of the other responses.

    :param http_status: The recommended HTTP status code to respond with,
                        if using HTTP for transport.
    :param request_id: This member is REQUIRED. It MUST be the same as the
                       value of the id member in the Request Object. If
                       there was an error in detecting the id in the Request
                       object (e.g. Parse error/Invalid Request), it MUST be
                       Null.
    """

    def __init__(self, http_status, request_id):
        #: Holds the HTTP status code to respond with (if using HTTP).
        self.http_status = http_status
        #: The 'id' part from the request to be sent back in the response.
        self.request_id = request_id

    @property
    def json(self):
        """Must be overridden in subclasses."""
        raise NotImplementedError()

    @property
    def json_debug(self):
        """JSON-RPC response, in dictionary form."""
        return self.json

    @property
    def body(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self.json)) if self.json else ''

    @property
    def body_debug(self):
        """JSON-RPC response string."""
        return self.body


class ErrorResponse(_Response):
    """Returned from `dispatch()`_ if there was an error while processing the
    request.
    """

    def __init__(self, http_status, request_id, code, message, data=None):
        """
        :param http_status: The recommended HTTP status code to respond with, if
                            using HTTP for transport.
        :param request_id: Must be the same as the value as the id member in the
                           Request Object. If there was an error in detecting
                           the id in the Request object (e.g. Parse
                           error/Invalid Request), it MUST be Null.
        :param code: A Number that indicates the error type that occurred. This
                     MUST be an integer.
        :param message: A string providing a short description of the error, eg.
                        "Invalid params"
        :param data: A Primitive or Structured value that contains additional
                     information about the error. This may be omitted.
        """
        super(ErrorResponse, self).__init__(http_status, request_id)
        #: Holds the JSON-RPC error code.
        self.code = code
        #: Holds a one-line message describing the error.
        self.message = message
        #: Holds extra information about the error.
        self.data = data

    @property
    def json(self):
        """JSON-RPC response, in dictionary form."""
        return {'jsonrpc': '2.0', 'error': {
            'code': self.code, 'message': self.message}, 'id': self.request_id}

    @property
    def json_debug(self):
        """JSON-RPC response, in dictionary form, with ``data`` attribute
        included.
        """
        r = self.json
        r['error']['data'] = self.data
        return r

    @property
    def body_debug(self):
        """JSON-RPC response string, with ``data`` attribute included."""
        return json.dumps(_sort_response(self.json_debug))


class RequestResponse(_Response):
    """Returned from `dispatch()`_ in response to a "request" - i.e. a request
    that wants a response back - after processing successfully.
    """

    #: The HTTP status to send when responding to requests.
    http_status = status.HTTP_OK

    def __init__(self, request_id, result):
        """
        :param request_id: Matches the original request's id value.
        :param result:
            The payload from processing the request. If the request was a
            JSON-RPC notification (i.e. the request id is ``None``), the result
            must also be ``None`` because notifications don't require any data
            returned.
        """
        # Ensure we're not responding to a notification with data
        if not request_id:
            raise ValueError(
                'Requests must have an id, use NotificationResponse instead')
        super(RequestResponse, self).__init__(self.http_status, request_id)
        #: Holds the payload from processing the request successfully.
        self.result = result

    @property
    def json(self):
        """JSON-RPC response, in dictionary form."""
        if self.request_id:
            return {'jsonrpc': '2.0', 'result': self.result, 'id':
                    self.request_id}
        # else None


class NotificationResponse(_Response):
    """Returned from `dispatch()`_ in response to notifications."""

    #: The HTTP status to send in response to notifications. Default is ``204``,
    #: but some clients prefer to get ``200 OK``. Monkey patch to configure.
    http_status = status.HTTP_NO_CONTENT

    def __init__(self):
        super(NotificationResponse, self).__init__(self.http_status, None)

    @property
    def json(self):
        return None
