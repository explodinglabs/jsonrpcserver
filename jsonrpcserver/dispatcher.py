"""
Dispatcher.

The dispatch function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
import logging
from json import JSONDecodeError
from json import dumps as serialize
from json import loads as deserialize
from typing import Any, Dict, List, Optional, Union, cast

from jsonschema import ValidationError  # type: ignore
from jsonschema import validate as validate_jsonrpc  # type: ignore
from pkg_resources import resource_string

from .log import log_
from .methods import Methods, global_methods, validate_args
from .request import UNSPECIFIED, Request
from .response import (
    BatchResponse,
    ExceptionResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    InvalidParamsResponse,
    MethodNotFoundResponse,
    NotificationResponse,
    Response,
    SuccessResponse,
)
from .status import HTTP_STATUS_CODES
from .types import DeserializedRequest, DeserializedRequests, Method, Requests

request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")

schema = deserialize(resource_string(__name__, "request-schema.json"))

DEFAULT_REQUEST_LOG_FORMAT = "--> %(message)s"
DEFAULT_RESPONSE_LOG_FORMAT = "<-- %(message)s"


def log_request(request: str, trim_log_values: bool = False, **kwargs: Any) -> None:
    """Log a request"""
    return log_(request, request_logger, "info", trim=trim_log_values, **kwargs)


def log_response(
    response: Response, trim_log_values: bool = False, **kwargs: Any
) -> None:
    """Log a response"""
    return log_(str(response), response_logger, "info", trim=trim_log_values, **kwargs)


def is_batch_request(requests_deserialized):
    return isinstance(requests_deserialized, list)


def call(method: Method, *args: Any, **kwargs: Any) -> Any:
    """
    Returns:
        The result.

    Raises:
        TypeError: If arguments don't match function signature.
    """
    return validate_args(method, *args, **kwargs)(*args, **kwargs)


def dispatch_request(request: Request, methods: Methods, *, debug: bool) -> Response:
    """
    Call the appropriate method for a single request.

    Finds the method from the list of methods, call it, and return a Response.

    Args:
        request: A single Request object.
        methods: The Methods object containing all the available methods.
        debug: Include more information in error responses.

    Returns:
        A Response object.
    """
    try:
        result = call(methods.items[request.method], *request.args, **request.kwargs)
        return SuccessResponse(result=result, id=request.id)
    except KeyError:  # Method not found
        return MethodNotFoundResponse(id=request.id, data=request.method, debug=debug)
    except TypeError as exc:  # Validate args failed
        return InvalidParamsResponse(id=request.id, data=str(exc), debug=debug)
    except Exception as exc:  # Other error inside method - server error
        return ExceptionResponse(exc, id=request.id, debug=debug)
    finally:
        if request.is_notification:
            return NotificationResponse()


def dispatch_deserialized(
    requests: Union[Dict, List],
    methods: Methods,
    *,
    debug: bool,
    context: Any = UNSPECIFIED,
    convert_camel_case: bool,
) -> Response:
    """
    Takes a deserialized Python object.
    """
    try:
        validate_jsonrpc(requests, schema)
    except ValidationError as exc:
        return InvalidJSONRPCResponse(data=None, debug=debug)
    if isinstance(requests, list):
        return BatchResponse(
            dispatch_request(
                Request(
                    **request, context=context, convert_camel_case=convert_camel_case
                ),
                methods,
                debug=debug,
            )
            for request in requests
        )
    # Single request
    return dispatch_request(
        Request(**requests, context=context, convert_camel_case=convert_camel_case),
        methods,
        debug=debug,
    )


def dispatch_pure(
    requests: str,
    methods: Methods,
    *,
    convert_camel_case: bool,
    debug: bool,
    **kwargs: Any,
) -> Response:
    """
    Pure version of dispatch (no logging).

    Also "methods" is required here, unlike the public dispatch function.

    Args:
        request: The JSON-RPC request to process.
        convert_camel_case: Convert keys in params dictionary from camel case to
            snake case.
        debug: Include more information in error responses.

    Returns:
        A Response.
    """
    try:
        return dispatch_deserialized(
            deserialize(requests),
            methods,
            convert_camel_case=convert_camel_case,
            debug=debug,
            **kwargs,
        )
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc), debug=debug)


# @apply_config(config)
def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    *,
    basic_logging: bool = False,
    convert_camel_case: bool = False,
    debug: bool = False,
    trim_log_values: bool = False,
    **kwargs: Any,
) -> Response:
    """
    Dispatch a request (or requests) to methods.

    This is the main public method, it's the only one with optional params, and the only
    one that can be configured with a config file/env vars.

    Args:
        convert_camel_case: Convert keys in params dictionary from camel case to
            snake case.
        debug: Include more information in error responses.
        trim_log_values: Show abbreviated requests and responses in log.

    Returns:
        A Response.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', methods)
    """
    # Use the global methods object if no methods object was passed.
    methods = global_methods if methods is None else methods
    # Add temporary stream handlers for this request, and remove them later
    if basic_logging:
        # Request handler
        request_handler = logging.StreamHandler()
        request_handler.setFormatter(logging.Formatter(fmt=DEFAULT_REQUEST_LOG_FORMAT))
        request_logger.addHandler(request_handler)
        request_logger.setLevel(logging.INFO)
        # Response handler
        response_handler = logging.StreamHandler()
        response_handler.setFormatter(
            logging.Formatter(fmt=DEFAULT_RESPONSE_LOG_FORMAT)
        )
        response_logger.addHandler(response_handler)
        response_logger.setLevel(logging.INFO)
    log_request(request, trim_log_values=trim_log_values)
    response = dispatch_pure(
        request, methods, convert_camel_case=convert_camel_case, debug=debug, **kwargs
    )
    log_response(response, trim_log_values=trim_log_values)
    # Remove the temporary stream handlers
    if basic_logging:
        request_logger.handlers = [
            h for h in request_logger.handlers if h is not request_handler
        ]
        response_logger.handlers = [
            h for h in response_logger.handlers if h is not response_handler
        ]
    return response
