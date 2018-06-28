"""
The dispatch function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
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


def log_response(response, trim=None):
    """Log a response"""
    log(
        response_logger,
        logging.INFO,
        str(response),
        fmt="<-- %(message)s",
        extra={
            "http_code": response.http_status,
            "http_reason": HTTP_STATUS_CODES[response.http_status],
        },
        trim=trim,
    )
    return None


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


def dispatch(
    methods,
    requests,
    context=None,
    convert_camel_case=None,
    debug=None,
    notification_errors=None,
    schema_validation=None,
    trim_log_values=None
):
    """
    Dispatch a request to a method.

    >>> dispatch([ping], {'jsonrpc': '2.0', 'method': 'ping', 'id': 1})
    --> {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
    <-- {'jsonrpc': '2.0', 'result': 'pong', 'id': 1}
    'pong'

    :param methods: Collection of methods to dispatch to.
    :param requests: Requests to process.
    :param context: Optional context object which will be passed through to the methods.
    :param convert_camel_case: Convert keys in params dictionary from camel case to
        snake case.
    :param debug: Include more information in error responses.
    :param notification_errors: Respond with errors to notification requests (breaks
        the JSON-RPC specification, but I prefer to know about errors).
    :param schema_validation: Validate requests against the JSON-RPC schema.
    :param trim_log_values: Show abbreviated requests and responses in log.
    :returns: A :mod:`response` object.
    """
    # Some ugly code here to support the old config module which will be removed in 4.0,
    # and replaced with default arguments in the params of this function.
    convert_camel_case = (
        config.convert_camel_case if convert_camel_case is None else convert_camel_case
    )
    debug = config.debug if debug is None else debug
    notification_errors = (
        config.notification_errors
        if notification_errors is None
        else notification_errors
    )
    schema_validation = (
        config.schema_validation if schema_validation is None else schema_validation
    )
    trim_log_values = config.trim_log_values if trim_log_values is None else trim_log_values

    # TODO: Remove this predicate in version 4; configure logging Pythonically
    if config.log_requests:
        log(request_logger, logging.INFO, requests, fmt="--> %(message)s", trim=trim_log_values)

    try:
        requests = validate(load_from_json(requests))
    except JsonRpcServerError as exc:
        response = ExceptionResponse(exc, None, debug=debug)
    else:
        kwargs = dict(
            context=context,
            convert_camel_case=convert_camel_case,
            debug=debug,
            notification_errors=notification_errors,
            schema_validation=schema_validation,
        )
        if isinstance(requests, list):
            # Batch request
            responses = (Request(r, **kwargs).call(methods) for r in requests)
            # Remove notifications; batch request do not include them, as per spec
            responses = [r for r in responses if not r.is_notification]
            # If the response list is empty, return nothing
            response = BatchResponse(responses) if responses else NotificationResponse()
        # Single request
        else:
            response = Request(requests, **kwargs).call(methods)

    # TODO: Remove this predicate in version 4; configure logging Pythonically
    if config.log_responses:
        log_response(response, trim=trim_log_values)
    return response
