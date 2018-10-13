"""
Dispatcher.

The dispatch function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
import collections
import logging
import os
from configparser import ConfigParser
from json import JSONDecodeError
from json import loads as deserialize
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from apply_defaults import apply_config  # type: ignore
from jsonschema import ValidationError  # type: ignore
from jsonschema import validate as jsonschema_validate  # type: ignore
from pkg_resources import resource_string

from .log import log_
from .methods import Method, Methods, global_methods, validate_args
from .request import NOCONTEXT, Request
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

request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")

schema = deserialize(resource_string(__name__, "request-schema.json"))

DEFAULT_REQUEST_LOG_FORMAT = "--> %(message)s"
DEFAULT_RESPONSE_LOG_FORMAT = "<-- %(message)s"

config = ConfigParser(default_section="dispatch")
config.read([".jsonrpcserverrc", os.path.expanduser("~/.jsonrpcserverrc")])


def add_handlers() -> Tuple[logging.Handler, logging.Handler]:
    # Request handler
    request_handler = logging.StreamHandler()
    request_handler.setFormatter(logging.Formatter(fmt=DEFAULT_REQUEST_LOG_FORMAT))
    request_logger.addHandler(request_handler)
    request_logger.setLevel(logging.INFO)
    # Response handler
    response_handler = logging.StreamHandler()
    response_handler.setFormatter(logging.Formatter(fmt=DEFAULT_RESPONSE_LOG_FORMAT))
    response_logger.addHandler(response_handler)
    response_logger.setLevel(logging.INFO)
    return request_handler, response_handler


def remove_handlers(
    request_handler: logging.Handler, response_handler: logging.Handler
) -> None:
    request_logger.handlers = [
        h for h in request_logger.handlers if h is not request_handler
    ]
    response_logger.handlers = [
        h for h in response_logger.handlers if h is not response_handler
    ]


def log_request(request: str, trim_log_values: bool = False, **kwargs: Any) -> None:
    """Log a request"""
    return log_(request, request_logger, logging.INFO, trim=trim_log_values, **kwargs)


def log_response(response: str, trim_log_values: bool = False, **kwargs: Any) -> None:
    """Log a response"""
    return log_(response, response_logger, logging.INFO, trim=trim_log_values, **kwargs)


def validate(request: Union[Dict, List], schema: dict) -> Union[Dict, List]:
    """
    Wraps jsonschema.validate, returning the same object passed in.

    Raises:
        ValidationError
    """
    jsonschema_validate(request, schema)
    return request


def call(method: Method, *args: Any, **kwargs: Any) -> Any:
    """
    Returns:
        The "result" part of the JSON-RPC response (the return value from the method).

    Raises:
        TypeError: If arguments don't match function signature.
    """
    return validate_args(method, *args, **kwargs)(*args, **kwargs)


def safe_call(request: Request, methods: Methods, *, debug: bool) -> Response:
    """
    Call a Request, catching exceptions to always return a Response.
    """
    try:
        result = call(methods.items[request.method], *request.args, **request.kwargs)
    except KeyError:
        return MethodNotFoundResponse(id=request.id, data=request.method, debug=debug)
    except (TypeError, AssertionError) as exc:
        # Validate args failed - TypeError is raised by jsonschema, AssertionError
        # raised inside the methods.
        return InvalidParamsResponse(id=request.id, data=str(exc), debug=debug)
    except Exception as exc:  # Other error inside method - server error
        return ExceptionResponse(exc, id=request.id, debug=debug)
    finally:
        if request.is_notification:
            return NotificationResponse()
    return SuccessResponse(result=result, id=request.id)


def call_requests(
    requests: Union[Request, Iterable[Request]], methods: Methods, debug: bool
) -> Response:
    """
    Takes a request or list of Requests and calls them.
    """
    if isinstance(requests, collections.Iterable):
        return BatchResponse(safe_call(r, methods, debug=debug) for r in requests)
    return safe_call(requests, methods, debug=debug)


def create_requests(
    requests: Union[Dict, List], *, context: Any = NOCONTEXT, convert_camel_case: bool
) -> Union[Request, Iterable[Request]]:
    if isinstance(requests, list):
        return (
            Request(context=context, convert_camel_case=convert_camel_case, **request)
            for request in requests
        )
    return Request(context=context, convert_camel_case=convert_camel_case, **requests)


def dispatch_pure(
    request: str,
    methods: Methods,
    *,
    context: Any,
    convert_camel_case: bool,
    debug: bool,
) -> Response:
    """
    Pure version of dispatch - no logging, no optional parameters.

    Does two things:
        1. Deserializes and validates the string.
        2. Calls each request.

    Returns:
        A Response.
    """
    try:
        deserialized = validate(deserialize(request), schema)
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc), debug=debug)
    except ValidationError as exc:
        return InvalidJSONRPCResponse(data=None, debug=debug)
    return call_requests(
        create_requests(
            deserialized, context=context, convert_camel_case=convert_camel_case
        ),
        methods,
        debug=debug,
    )


@apply_config(config)
def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    *,
    basic_logging: bool = False,
    convert_camel_case: bool = False,
    context: Any = NOCONTEXT,
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
        request_handler, response_handler = add_handlers()
    log_request(request, trim_log_values=trim_log_values)
    response = dispatch_pure(
        request,
        methods,
        debug=debug,
        context=context,
        convert_camel_case=convert_camel_case,
    )
    log_response(str(response), trim_log_values=trim_log_values)
    # Remove the temporary stream handlers
    if basic_logging:
        remove_handlers(request_handler, response_handler)
    return response
