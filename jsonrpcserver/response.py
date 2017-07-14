"""
The return value from ``dispatch`` is a response object.

::

    >>> response = methods.dispatch(request)
    >>> response
    {'jsonrpc': '2.0', 'result': 'foo', 'id': 1}

Use ``str()`` to get a JSON-encoded string::

    >>> str(response)
    '{"jsonrpc": "2.0", "result": "foo", "id": 1}'

There's also an HTTP status code if you need it::

    >>> response.http_status
    200
"""
from collections import OrderedDict
import json

from . import status, config
from .exceptions import JsonRpcServerError, ServerError


def _sort_response(response):
    """
    Sort the keys in a JSON-RPC response object.

    This has no effect other than making it nicer to read.

    Example::

        >>> json.dumps(_sort_response({'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
        {"jsonrpc": "2.0", "result": 5, "id": 1}

    :param response: JSON-RPC response, in dictionary form.
    :return: The same response, sorted in an ``OrderedDict``.
    """
    root_order = ['jsonrpc', 'result', 'error', 'id']
    error_order = ['code', 'message', 'data']
    req = OrderedDict(sorted(
        response.items(), key=lambda k: root_order.index(k[0])))
    if 'error' in response:
        req['error'] = OrderedDict(sorted(
            response['error'].items(), key=lambda k: error_order.index(k[0])))
    return req


class Response(object):
    """Base class of all responses."""
    is_notification = False

    def __str__(self):
        raise NotImplementedError()


class RequestResponse(Response, dict):
    """
    Response returned from a Request.

    Returned from processing a successful request with an ``id`` member,
    (indicating that a payload is expected back).
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


class ErrorResponse(Response, dict):
    """
    Error response.

    Returned if there was an error while processing the request.
    """
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
        if config.debug and data:
            self['error']['data'] = data
        #: The recommended HTTP status code. (the status code depends on the
        #: error)
        self.http_status = http_status

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(_sort_response(self))


class ExceptionResponse(ErrorResponse):
    """Returns an ErrorResponse built from an exception."""

    def __init__(self, ex, request_id):
        if not isinstance(ex, JsonRpcServerError):
            ex = ServerError(str(ex))
        super(ExceptionResponse, self).__init__(
            ex.http_status, request_id, ex.code, ex.message, ex.data)


class NotificationResponse(Response):
    """
    Notification response.

    Returned from processing a successful `notification
    <http://www.jsonrpc.org/specification#notification>`_ (i.e. a request with
    no ``id`` member).
    """
    #: This is the only notification
    is_notification = True
    #: The HTTP status to send in response to notifications.
    http_status = status.HTTP_NO_CONTENT

    def __str__(self):
        return ''


class BatchResponse(Response, list):
    """
    Returned from batch requests.

    Basically a collection of responses.
    """
    http_status = status.HTTP_OK

    def __str__(self):
        """JSON-RPC response string."""
        return json.dumps(self)
