"""
Dispatcher

Takes JSON-RPC requests, logs them, calls the appropriate method, then logs and returns
the response.
"""
import json
import logging

from six import string_types

from . import config
from .exceptions import JsonRpcServerError, ParseError, InvalidRequest
from .log import log
from .request import Request
from .response import NotificationResponse, ExceptionResponse, BatchResponse
from .status import HTTP_STATUS_CODES


request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")


def log_response(response):
    """Log a response"""
    log(
        response_logger,
        "info",
        str(response),
        fmt="<-- %(message)s",
        extra={
            "http_code": response.http_status,
            "http_reason": HTTP_STATUS_CODES[response.http_status],
        },
    )


def load_from_json(requests):
    """
    Load from string to a Python dictionary, or list in the case of a batch request.

    :param request: The JSON-RPC request string.
    :raises ValueError: If the string cannot be parsed to JSON.
    :returns: The same request in dict form.
    """
    if isinstance(requests, string_types):
        try:
            requests = json.loads(requests)
        except ValueError:
            raise ParseError()
    return requests


def validate(requests):
    # Empty batch requests are invalid http://www.jsonrpc.org/specification#examples
    if isinstance(requests, list) and not requests:
        raise InvalidRequest()
    return requests


def dispatch(methods, requests, context=None):
    """
    Process a request.

    .. code-block:: python

        >>> request = {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
        >>> response = dispatch([ping], request)
        --> {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
        <-- {'jsonrpc': '2.0', 'result': 'pong', 'id': 1}

    :param methods: Collection of methods to dispatch to.
    :param requests: Requests to process.
    :param context: Optional context object which will be passed through to the methods.
    :returns: A :mod:`response` object.
    """
    if config.log_requests:
        log(request_logger, "info", requests, fmt="--> %(message)s")
    try:
        requests = validate(load_from_json(requests))
    except JsonRpcServerError as exc:
        response = ExceptionResponse(exc, None)
    else:
        # Batch requests
        if isinstance(requests, list):
            response = [Request(r, context=context).call(methods) for r in requests]
            # Responses to batch requests should not contain notifications, as per spec
            response = [r for r in response if not r.is_notification]
            # If the response list is empty, return nothing
            response = BatchResponse(response) if response else NotificationResponse()
        # Single request
        else:
            response = Request(requests, context=context).call(methods)
    if config.log_responses:
        log_response(response)
    return response
