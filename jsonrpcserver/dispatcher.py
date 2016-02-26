"""
Dispatcher
**********
"""

import logging
import json

from six import string_types

from jsonrpcserver.response import NotificationResponse, ExceptionResponse, \
    BatchResponse
from jsonrpcserver.request import Request
from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest
from jsonrpcserver.status import HTTP_STATUS_CODES

logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')


def _string_to_dict(request):
    """Convert a JSON-RPC request string, to a dictionary.

    :param request: The JSON-RPC request string.
    :raises ValueError: If the string cannot be parsed to JSON.
    :returns: The same request in dict form.
    """
    try:
        return json.loads(request)
    except ValueError:
        raise ParseError()


def dispatch(methods, request):
    """Dispatch JSON-RPC requests to a collection of methods::

        r = dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

    The first parameter can be either:

    - A *list* of methods, or
    - A *dictionary* of name:method pairs.

    When using a **list**, the methods must be identifiable by a ``__name__``
    attribute.

    Functions already have a ``__name__`` attribute::

        >>> def cat():
        ...     return 'meow'
        ...
        >>> cat.__name__
        'cat'
        >>> dispatch([cat], ...)

    Lambdas require setting it::

        >>> cat = lambda: 'meow'
        >>> cat.__name__ = 'cat'
        >>> dispatch([cat], ...)

    As do partials::

        >>> max_ten = partial(min, 10)
        >>> max_ten.__name__ = 'max_ten'
        >>> dispatch([max_ten], ...)

    Alternatively, use a **dictionary**::

        >>> dispatch({'cat': cat, 'max_ten': max_ten}, ...)

    The :mod:`methods` module also gives nice and easy ways to build the
    collection of methods.

    :param methods:
        Collection of methods to dispatch to.
    :param request:
        JSON-RPC request - can be a JSON-serializable object, or a string.
        Strings must be valid json (use double quotes!).
    :returns:
        A :mod:`response` object.
    """
    # Process the request
    response = None
    try:
        # Log the request
        request_log.info(request)
        # If the request is a string, convert it to a dict first
        if isinstance(request, string_types):
            request = _string_to_dict(request)
        # Batch requests
        if isinstance(request, list):
            # An empty list is invalid
            if len(request) == 0:
                raise InvalidRequest()
            # Process each request
            response = BatchResponse()
            for r in request:
                try:
                    req = Request(r)
                except InvalidRequest as e:
                    resp = ExceptionResponse(e, None)
                else:
                    resp = req.process(methods)
                response.append(resp)
            # Remove Notification responses
            response = BatchResponse(
                [r for r in response if not isinstance(
                    r, NotificationResponse)])
            # "Nothing is returned for all notification batches"
            if not response:
                response = NotificationResponse() # pylint: disable=redefined-variable-type
        # Single request
        else:
            response = Request(request).process(methods)
    except JsonRpcServerError as e:
        response = ExceptionResponse(e, None)
    # Batch requests can have mixed results, just return 200
    http_status = 200 if isinstance(request, list) else response.http_status
    # Log the response
    response_log.info(str(response), extra={
        'http_code': http_status,
        'http_reason': HTTP_STATUS_CODES[http_status]})
    return response
