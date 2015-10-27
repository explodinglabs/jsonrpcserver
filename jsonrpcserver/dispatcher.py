"""
Dispatcher
**********

.. _RequestResponse: #response.RequestResponse
.. _NotificationResponse: #response.NotificationResponse
.. _ErrorResponse: #response.ErrorResponse
"""

import logging

from funcsigs import signature

from jsonrpcserver.response import RequestResponse, NotificationResponse, \
    ErrorResponse
from jsonrpcserver.request import Request
from jsonrpcserver.exceptions import JsonRpcServerError, InvalidParams, \
    ServerError
from jsonrpcserver.status import HTTP_STATUS_CODES
from jsonrpcserver.methods import _get_method

logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')


def _validate_arguments_against_signature(func, args, kwargs):
    """Check if arguments match a function signature and can therefore be passed
    to it.

    :param func: The function object.
    :param args: List of positional arguments (or None).
    :param kwargs: Dict of keyword arguments (or None).
    :raises InvalidParams: If the arguments cannot be passed to the function.
    """
    try:
        if not args and not kwargs:
            signature(func).bind()
        elif args:
            signature(func).bind(*args)
        elif kwargs:
            signature(func).bind(**kwargs)
    except TypeError as e:
        raise InvalidParams(str(e))


def _call(methods, method_name, args=None, kwargs=None):
    """Find a method from a list, then validate the arguments before calling it.

    :param methods: The list of methods - either a python list, or Methods obj.
    :param args: Positional arguments (list)
    :param kwargs: Keyword arguments (dict)
    :raises MethodNotFound: If the method is not in the list.
    :raises InvalidParams: If the arguments don't match the method signature.
    :returns: The return value from the method called.
    """
    # Get the method object from a list of rpc methods
    method = _get_method(methods, method_name)
    # Ensure the arguments match the method's signature
    _validate_arguments_against_signature(method, args, kwargs)
    # Call the method
    if args and kwargs:
        # Cannot have both positional and keyword arguments in JSON-RPC.
        raise InvalidParams()
    elif not args and not kwargs:
        return method()
    elif args:
        return method(*args)
    elif kwargs:
        return method(**kwargs)


def dispatch(methods, request, notification_errors=False):
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
    :param notification_errors:
        Should `notifications
        <http://www.jsonrpc.org/specification#notification>`_ get error
        responses? Typically notifications don't receive any response, except
        for "Parse error" and "Invalid request" errors. Enabling this will
        include all other errors such as "Method not found". A notification is
        then similar to many unix commands - *"There was no response, so I can
        assume the request was successful."*
    :returns: A `Response`_ object - either `RequestResponse`_,
              `NotificationResponse`_, or `ErrorResponse`_ if there was a
              problem processing the request. In any case, the return value
              gives you ``body``, ``body_debug``, ``json``, ``json_debug``, and
              ``http_status`` values.
    """

    # Process the request
    r = None
    error = None
    try:
        # Log the request
        request_log.info(str(request))
        # Create request object (also validates the request)
        r = Request(request)
        # Call the requested method
        result = _call(methods, r.method_name, r.args, r.kwargs)
    # Catch any JsonRpcServerError raised (Invalid Request, etc)
    except JsonRpcServerError as e:
        error = e
    # Catch uncaught exceptions, respond with ServerError
    except Exception as e: # pylint: disable=broad-except
        # Log the uncaught exception
        logger.exception(e)
        # Create an exception object, used to build the response
        error = ServerError(str(e))

    # Now build a response.
    # Error
    if error:
        # Notifications get a non-response - see spec
        if r and r.is_notification and not notification_errors:
            response = NotificationResponse()
        else:
            # Get the 'id' part of the request, to include in error response
            request_id = r.request_id if r else None
            response = ErrorResponse(
                error.http_status, request_id, error.code, error.message,
                error.data)
    # Success
    else:
        # Notifications get a non-response
        if r and r.is_notification:
            response = NotificationResponse()
        else:
            response = RequestResponse(r.request_id, result)

    # Log the response and return it
    response_log.info(response.body, extra={
        'http_code': response.http_status,
        'http_reason': HTTP_STATUS_CODES[response.http_status]})
    return response
