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
    """Dispatch a JSON-RPC request to a collection of methods::

        >>> dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

    The first parameter can be either a list of methods as above, or a
    dictionary of name:method pairs:

        >>> dispatch({'cat': cat, 'max_ten': max_ten}, ...)

    If you have more than a few methods, look into the :class:`~methods.Methods`
    class.

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
