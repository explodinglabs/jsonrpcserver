"""
Response
********

The response objects returned by `dispatch()`_.

.. _dispatch(): #dispatcher.dispatch
"""

import json
from collections import OrderedDict
from jsonrpcserver import status
from jsonrpcserver.exceptions import JsonRpcServerError, ServerError


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


class NotificationResponse(_Response):
    """Returned from `dispatch()`_ in response to notifications."""

    #: The HTTP status to send in response to notifications. Default is ``204``,
    #: but some clients prefer to get ``200 OK``. Monkey patch to configure.
    http_status = status.HTTP_NO_CONTENT

    def __str__(self):
        return ''


class _Response(dict):
    """Parent of the other responses.

    :param request_id:
        This member is REQUIRED. It MUST be the same as the value of the id
        member in the Request Object. If there was an error in detecting the id
        in the Request object (e.g. Parse error/Invalid Request), it MUST be
        Null.
    """

    def __str__(self):
        raise NotImplemented()


class RequestResponse(_Response):
    """Returned from `dispatch()`_ in response to a "request", (i.e. a request
    that wants a response back), after processing successfully.
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
        self['jsonrpc'] = '2.0'
        self['id'] = request_id
        #: Holds the payload from processing the request successfully.
        self['result'] = result

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self))


class ErrorResponse(_Response):
    """Returned from `dispatch()`_ if there was an error while processing the
    request.
    """
    debug = False
    notification_errors = False

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
        self['jsonrpc'] = '2.0'
        self['id'] = request_id
        self['error'] = dict()
        #: Holds the JSON-RPC error code.
        self['error']['code'] = code
        #: Holds a one-line message describing the error.
        self['error']['message'] = message
        #: Holds extra information about the error.
        if self.debug and data:
            self['error']['data'] = data
        #: Holds the recommended HTTP status to respond with (if using HTTP).
        self.http_status = http_status

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self))


class ExceptionResponse(ErrorResponse):
    """Returns an ErrorResponse built from an exception"""
    def __init__(self, ex, request_id):
        if not isinstance(ex, JsonRpcServerError):
            ex = ServerError(str(ex))
        super(ExceptionResponse, self).__init__(ex.http_status, request_id,
            ex.code, ex.message, ex.data)


class BatchResponse(list):

    http_status = status.HTTP_OK

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(self)
