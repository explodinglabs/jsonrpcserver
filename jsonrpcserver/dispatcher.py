"""At the core of jsonrpcserver is the dispatcher, which processes JSON-RPC
requests.

::

    from jsonrpcserver import dispatch
"""
import logging
import json

from six import string_types

from jsonrpcserver.log import _log
from jsonrpcserver.response import NotificationResponse, ExceptionResponse, \
    BatchResponse
from jsonrpcserver.request import Request
from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest
from jsonrpcserver.status import HTTP_STATUS_CODES

_request_log = logging.getLogger(__name__+'.request')
_response_log = logging.getLogger(__name__+'.response')


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
    # pylint:disable=line-too-long
    """Process a JSON-RPC request, calling the requested method.

    .. code-block:: python

        >>> request = {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
        >>> response = dispatch({'ping': lambda: 'pong'}, request)
        --> {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
        <-- {'jsonrpc': '2.0', 'result': 'pong', 'id': 1}

    :param methods:
        Collection of methods to dispatch to. Can be a ``list`` of functions, a
        ``dict`` of name:method pairs, or a ``Methods`` object.
    :param request:
        A JSON-RPC request. Can be a JSON-serializable object, or a string.
        (Strings must be valid JSON - use double quotes!)
    :returns:
        A :mod:`response` object.
    """
    # Process the request
    response = None
    try:
        # Log the request
        _log(_request_log, 'info', request, fmt='--> %(message)s')
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
    _log(_response_log, 'info', str(response), fmt='<-- %(message)s', extra={
        'http_code': http_status,
        'http_reason': HTTP_STATUS_CODES[http_status]})
    return response
