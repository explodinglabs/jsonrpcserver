"""
Dispatcher
**********

.. _RequestResponse: #response.RequestResponse
.. _NotificationResponse: #response.NotificationResponse
.. _ErrorResponse: #response.ErrorResponse
"""

import logging
import json

from six import string_types

from jsonrpcserver.response import _Response, RequestResponse, \
    NotificationResponse, ErrorResponse, ExceptionResponse
from jsonrpcserver.request import Request
from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest, ServerError
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
    """Dispatch JSON-RPC requests to a list of methods::

        r = dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

    The first parameter can be either:

    - A *list* of functions, each identifiable by its ``__name__`` attribute.
    - Or a *dictionary* of name:method pairs.

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

    Alternatively, consider using a **dictionary** instead::

        >>> dispatch({'cat': cat, 'max_ten': max_ten}, ...)

    See the `Methods`_ module for another easy way to build the list of methods.

    :param methods: List or dict of methods to dispatch to.
    :param request:
        JSON-RPC request. This can be in dict or string form.  Byte arrays
        should be `decoded
        <https://docs.python.org/3/library/codecs.html#codecs.decode>`_ first.
    :returns: A `Response`_ object, or for batch requests, a list of responses.
              The responses themselves are either `RequestResponse`_,
              `NotificationResponse`_, or `ErrorResponse`_ if there was a
              problem processing the request. In any case, the return value
              gives you ``body``, ``body_debug``, ``json``, ``json_debug``, and
              ``http_status`` attributes.
    """
    # Process the request
    error = None
    response = None
    try:
        # Log the request
        request_log.info(str(request))
        # If the request is a string, convert it to a dict first
        if isinstance(request, string_types):
            request = _string_to_dict(request)
        # Batch requests
        if isinstance(request, list):
            # An empty list should return Invalid Request
            if 0 == len(request):
                raise InvalidRequest()
            # Process each request
            response = list()
            for r in request:
                try:
                    req = Request(r)
                except InvalidRequest as e:
                    resp = ExceptionResponse(e, None)
                else:
                    resp = req.process(methods)
                response.append(resp)
            # Remove Notification responses
            response = [r for r in response if not isinstance(r,
                NotificationResponse)]
            # "Nothing is returned for all notification batches"
            if not response:
                response = NotificationResponse()
        # Single request
        else:
            response = Request(request).process(methods)
    except JsonRpcServerError as e:
        response = ExceptionResponse(e, None)
    except Exception as e: # pylint: disable=broad-except
        # Log the uncaught exception
        logger.exception(e)
        response = ExceptionResponse(e, None)
#    assert isinstance(response, _Response) \
#        or all([isinstance(r, _Response) for r in response])
    http_status = 200 if isinstance(request, list) else response.http_status
    response_log.info(str(response), extra={
        'http_code': http_status,
        'http_reason': HTTP_STATUS_CODES[http_status]})
    return response
