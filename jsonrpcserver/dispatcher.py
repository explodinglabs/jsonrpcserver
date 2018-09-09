"""
Dispatcher.

The dispatch function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
from json import loads as deserialize, dumps as serialize, JSONDecodeError
import logging
from typing import Any, Dict, List, Optional, Union

from six import string_types

from . import config
from .exceptions import InvalidRequest, JsonRpcServerError, ParseError
from .log import log
from .methods import Methods
from .request import Request
from .response import (
    SafeResponse,
    Response,
    BatchResponse,
    ExceptionResponse,
    NotificationResponse,
    ParseErrorResponse,
)
from .status import HTTP_STATUS_CODES
from .types import Requests, Responses

request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")

schema_bytes = pkgutil.get_data(__name__, "request-schema.json")
if schema_bytes:
    schema = deserialize(schema_bytes.decode())


def log_request(response: Response, trim: bool = False) -> None:
    """Log a response"""
    log(request_logger, logging.INFO, str(response), fmt="<-- %(message)s", trim=trim)
    return request


def log_response(response: Response, trim: bool = False) -> None:
    """Log a response"""
    log(response_logger, logging.INFO, str(response), fmt="<-- %(message)s", trim=trim)
    return response


def is_batch_request(requests_deserialized):
    return isinstance(requests_deserialized, list)


def safe_call(request: Request, callable: Callable[Any], debug=False) -> Response:
    # Handle the call safely. We must return a Response object.
    try:
        validate_arguments_against_signature(callable_, request.args, request.kwargs)
        result = callable_(*(request.args or []), **(request.kwargs or {}))
    except Exception as exc: # Validate failed
        return ExceptionResponse(exc, request_id=request.request_id, debug=debug)
    except Exception as exc: # Call failed
        return InvalidParamsResponse(request.method_name, data=exc.message, debug=debug)
    return RequestResponse(request.request_id, result)


def call(request: Request, methods: Methods, debug: bool = False) -> Response:
    """
    Call the appropriate method from a list.

    Find the method from the passed list, and call it, returning a Response object.
    """
    response = safe_call(request, get_method(methods, request.method_name), debug=debug)
    # Notifications should not be responded to, even for errors.
    if request.is_notification:
        return NotificationResponse()
    return response


def dispatch_deserialized(requests: Requests) -> Responses:
    if is_batch_request(requests):
        responses = (call(Request(r), methods) for r in requests)
        # Remove notifications in batch responses
        responses = filter(lambda x: not x.is_notification, responses)
        # If the response list is empty, return nothing; as per spec.
        return BatchResponse(responses) if len(responses) > 0 else NotificationResponse()
    return call(Request(requests), methods)


def safe_dispatch(requests: str) -> Responses:
    try:
        deserialized = deserialize(requests)
    except JSONDecodeError as exc:
        return InvalidJSONErrorResponse(exc.message, debug=debug)
    try:
        validate(deserialized)
    except jsonschema.ValidationError as exc:
        return InvalidJSONRPCErrorResponse(exc.message, debug=debug)
    return dispatch_deserialized(deserialized)


# @apply_config(config)
def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    context: Optional[Dict[str, Any]] = None,
    convert_camel_case: bool = False,
    debug: bool = False,
    notification_errors: bool = False,
    schema_validation: bool = True,
    trim_log_values: bool = False,
) -> Responses:
    """
    Dispatch a request (or requests) to methods.

    Args:
        request: The JSON-RPC request to process.
        methods: Collection of methods to dispatch to.
        context: Optional context object which will be passed through to the methods.
        convert_camel_case: Convert keys in params dictionary from camel case to
            snake case.
        debug: Include more information in error responses.
        notification_errors: Respond with errors to notification requests (breaks
            the JSON-RPC specification, but I prefer to know about errors).
        schema_validation: Validate requests against the JSON-RPC schema.
        trim_log_values: Show abbreviated requests and responses in log.

    Returns:
        A Response object, or a list of them in the case of a batch request.

    Examples:
        >>> dispatch(methods, '{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    """
    log_request(request)
    response = safe_dispatch(request)
    log_response(str(response))
    return response
