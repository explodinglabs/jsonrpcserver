"""
Response
********

These are the response objects returned by :func:`dispatch()
<dispatcher.dispatch>`.

As per the `specification
<http://www.jsonrpc.org/specification#response_object>`__, the type of response
depends on the type of request, and the result of processing it. For example,
after successfully processing a request with an ``id``, the payload data is in
``response['result']``.  Use ``str(response)`` to get a JSON-serialized string.
An additional ``http_status`` attribute has a suggested status code to respond
with (useful if using HTTP).
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
    r = OrderedDict(sorted(
        response.items(), key=lambda k: root_order.index(k[0])))
    if 'error' in response:
        r['error'] = OrderedDict(sorted(
            response['error'].items(), key=lambda k: error_order.index(k[0])))
    return r


class NotificationResponse(object):
    """Returned to a `Notification
    <http://www.jsonrpc.org/specification#notification>`_.
    """

    #: The HTTP status to send in response to notifications. Default is ``204``,
    #: but some clients do prefer ``200 OK``. Modify to configure.
    http_status = status.HTTP_NO_CONTENT

    def __str__(self):
        return ''


class _Response(dict):
    """Parent of the other responses."""

    def __str__(self):
        raise NotImplementedError()


class RequestResponse(_Response):
    """Returned to a request with an ``id`` member (indicating that a payload is
    expected).
    """

    #: The recommended HTTP status code.
    http_status = status.HTTP_OK

    def __init__(self, request_id, result):
        """
        :param request_id:
            Matches the original request's id value.
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
        super(RequestResponse, self).__init__(
            {'jsonrpc': '2.0', 'result': result, 'id': request_id})

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self))


class ErrorResponse(_Response):
    """Returned if there was an error while processing the request.
    """
    #: Should we include the ``data`` member when sending an error back to
    #: the client? It holds extra details about the error, for example if
    #: ``ServerError('Database error')`` was raised, it would hold ``'Database
    #: error'``. Modify to configure.
    debug = False
    #: Should we respond to notifications if there's an error, such as *Method
    #: not found*? The specification says no. Modify to configure.
    notification_errors = False

    def __init__(self, http_status, request_id, code, message, data=None):
        """
        :param http_status:
            The recommended HTTP status code.
        :param request_id:
            Must be the same as the value as the id member in the Request
            Object. If there was an error in detecting the id in the Request
            object (e.g. Parse error/Invalid Request), it MUST be Null.
        :param code:
            A Number that indicates the error type that occurred. This MUST be
            an integer.
        :param message:
            A string providing a short description of the error, eg.  "Invalid
            params"
        :param data:
            A Primitive or Structured value that contains additional information
            about the error. This may be omitted.
        """
        super(ErrorResponse, self).__init__(
            {'jsonrpc': '2.0', 'error': {'code': code, 'message': message},
             'id': request_id})
        #: Holds extra information about the error.
        if self.debug and data:
            self['error']['data'] = data
        #: The recommended HTTP status code.
        self.http_status = http_status

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self))


class ExceptionResponse(ErrorResponse):
    """Returns an ErrorResponse built from an exception"""
    def __init__(self, ex, request_id):
        if not isinstance(ex, JsonRpcServerError):
            ex = ServerError(str(ex))
        super(ExceptionResponse, self).__init__(
            ex.http_status, request_id, ex.code, ex.message, ex.data)


class BatchResponse(list):
    """Returned to batch requests. Basically a list of the other response
    objects.
    """

    http_status = status.HTTP_OK

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(self)
