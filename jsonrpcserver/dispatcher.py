"""
Dispatcher.

The dispatch() function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
import logging
import os
from collections.abc import Iterable
from configparser import ConfigParser
from json import JSONDecodeError
from json import dumps as default_serialize, loads as default_deserialize
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    cast,
)

from apply_defaults import apply_config  # type: ignore
from jsonschema import ValidationError  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pkg_resources import resource_string

from .log import log_
from .methods import Methods, global_methods, validate_args
from .request import Request, is_notification, NOID
from .response import (
    BatchResponse,
    ExceptionResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    InvalidParamsResponse,
    MethodNotFoundResponse,
    NotificationResponse,
    Response,
)

Context = NamedTuple(
    "Context",
    [("request", Request), ("extra", Any)],
)

request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")

DEFAULT_REQUEST_LOG_FORMAT = "--> %(message)s"
DEFAULT_RESPONSE_LOG_FORMAT = "<-- %(message)s"

# Prepare the jsonschema validator
schema = default_deserialize(resource_string(__name__, "request-schema.json"))
klass = validator_for(schema)
klass.check_schema(schema)
validator = klass(schema)

# Read configuration file
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

    Args:
        request: The deserialized-from-json request.
        schema: The jsonschema schema to validate against.

    Raises:
        jsonschema.ValidationError
    """
    validator.validate(request)
    return request


def c(request, method, *args, **kwargs) -> Response:
    errors = validate_args(method, *args, **kwargs)
    return (
        method(*args, **kwargs)
        if not errors
        else InvalidParamsResponse(data=errors, id=request.id)
    )


def call(request: Request, method: Callable, *, extra: Any) -> Response:
    return (
        c(
            request,
            method,
            *([Context(request=request, extra=extra)] + request.params),
        )
        if isinstance(request.params, list)
        else c(
            request,
            method,
            Context(request=request, extra=extra),
            **request.params,
        )
    )


def safe_call(
    request: Request, methods: Methods, *, extra: Any, serialize: Callable
) -> Response:
    """
    Call a Request, catching exceptions to ensure we always return a Response.

    Args:
        request: The Request object.
        methods: The list of methods that can be called.
        serialize: Function that is used to serialize data.

    Returns:
        A Response object.
    """
    if request.method in methods.items:
        try:
            response = call(request, methods.items[request.method], extra=extra)
        except Exception as exc:  # Other error inside method - server error
            logging.exception(exc)
            return ExceptionResponse(exc, id=request.id)
        else:
            return NotificationResponse() if is_notification(request) else response
    else:
        return MethodNotFoundResponse(data=request.method, id=request.id)


def dispatch_requests_pure(
    requests: Union[Request, Iterable[Request]],
    methods: Methods,
    *,
    extra: Any,
    serialize: Callable,
) -> Response:
    """
    Takes a request or list of Requests and calls them.

    Args:
        requests: Request object, or a collection of them.
        methods: The list of methods that can be called.
        serialize: Function that is used to serialize data.
    """
    return (
        BatchResponse(
            [
                safe_call(r, methods=methods, extra=extra, serialize=serialize)
                for r in requests
            ],
            serialize_func=serialize,
        )
        if isinstance(requests, list)
        else safe_call(
            cast(Request, requests),
            methods,
            extra=extra,
            serialize=serialize,
        )
    )


def dispatch_requests(
    requests: Union[Request, Iterable[Request]],
    methods: Methods,
    *,
    extra: Optional[Any] = None,
    serialize: Callable = default_serialize,
) -> Response:
    """
    Impure (public) version of dispatch_requests_pure - has default values.
    """
    return dispatch_requests_pure(requests, methods, extra=extra, serialize=serialize)


def create_requests(
    requests: Union[Dict, List[Dict]],
) -> Union[Request, List[Request]]:
    """
    Converts a raw deserialized request dictionary to a Request (namedtuple).

    Args:
        requests: Request dict, or a list of dicts.

    Returns:
        A Request object, or a list of them.
    """
    return (
        [
            Request(
                method=request["method"],
                params=request.get("params", []),
                id=request.get("id", NOID),
            )
            for request in requests
        ]
        if isinstance(requests, list)
        else Request(
            method=requests["method"],
            params=requests.get("params", []),
            id=requests.get("id", NOID),
        )
    )


def dispatch_pure(
    request: str,
    methods: Methods,
    *,
    extra: Any,
    serialize: Callable,
    deserialize: Callable,
) -> Response:
    """
    Pure version of dispatch - no logging, no optional parameters.

    Does two things:
        1. Deserializes and validates the string.
        2. Calls each request.

    Args:
        request: The incoming request string.
        methods: Collection of methods that can be called.
        extra: Will be included in the context dictionary passed to methods.
        serialize: Function that is used to serialize data.
        deserialize: Function that is used to deserialize data.
    Returns:
        A Response.
    """
    try:
        deserialized = validate(deserialize(request), schema)
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc))
    except ValidationError as exc:
        return InvalidJSONRPCResponse(data=None)
    else:
        return dispatch_requests_pure(
            create_requests(deserialized),
            methods=methods,
            extra=extra,
            serialize=serialize,
        )


@apply_config(config)
def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    *,
    basic_logging: bool = False,
    extra: Optional[Any] = None,
    trim_log_values: bool = False,
    serialize: Callable = default_serialize,
    deserialize: Callable = default_deserialize,
    **kwargs: Any,
) -> Response:
    """
    Dispatch a request (or requests) to methods.

    This is the main public method, it's the only one with optional params, and the only
    one that can be configured with a config file/env vars.

    Args:
        request: The incoming request string.
        methods: Collection of methods that can be called. If not passed, uses the
            internal methods object.
        extra: Extra data available inside methods (as context.extra).
        trim_log_values: Show abbreviated requests and responses in log.
        serialize: Function that is used to serialize data.
        deserialize: Function that is used to deserialize data.

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
        extra=extra,
        serialize=serialize,
        deserialize=deserialize,
    )
    log_response(str(response), trim_log_values=trim_log_values)
    # Remove the temporary stream handlers
    if basic_logging:
        remove_handlers(request_handler, response_handler)
    return response
