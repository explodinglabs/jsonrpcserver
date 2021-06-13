"""
Dispatcher.

The dispatch() function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
import logging
import os
from configparser import ConfigParser
from json import JSONDecodeError
from json import loads as default_deserialize
from typing import (
    Any,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Union,
    cast,
)

from apply_defaults import apply_config  # type: ignore
from jsonschema import ValidationError  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pkg_resources import resource_string

from .methods import Methods, global_methods, validate_args
from .request import Request, NOID
from .response import (
    InvalidRequestResponse,
    MethodNotFoundResponse,
    ParseErrorResponse,
    Response,
    ServerErrorResponse,
    from_result,
    should_respond,
    to_json,
)
from .result import InvalidParams, InternalError, Result

Context = NamedTuple(
    "Context",
    [("request", Request), ("extra", Any)],
)

request_logger = logging.getLogger(__name__ + ".request")
response_logger = logging.getLogger(__name__ + ".response")

DEFAULT_REQUEST_LOG_FORMAT = "--> %(message)s"
DEFAULT_RESPONSE_LOG_FORMAT = "<-- %(message)s"

# Prepare the jsonschema validator
global_schema = default_deserialize(resource_string(__name__, "request-schema.json"))
klass = validator_for(global_schema)
klass.check_schema(global_schema)
validator = klass(global_schema)

# Read configuration file
config = ConfigParser(default_section="dispatch")
config.read([".jsonrpcserverrc", os.path.expanduser("~/.jsonrpcserverrc")])


def call(method: Callable, args: list, kwargs: dict) -> Result:
    """
    Calls a method.

    Catches exceptions to ensure we always return a Response.

    Returns:
        The Result from the method call.
    """
    errors = validate_args(method, *args, **kwargs)
    if errors:
        return InvalidParams(errors)

    try:
        return method(*args, **kwargs)
    except Exception as exc:  # Other error inside method - server error
        logging.exception(exc)
        return InternalError(str(exc))


def extract_args(request: Request, extra: Any) -> list:
    return (
        [Context(request, extra)] + request.params
        if isinstance(request.params, list)
        else [Context(request, extra)]
    )


def extract_kwargs(request: Request) -> dict:
    return request.params if isinstance(request.params, dict) else {}


def dispatch_request(methods: Methods, extra: Any, request: Request) -> Response:
    """
    Dispatch a single Request.

    Maps a single Request to a single Response.

    Converts the return value (a Result) into a Response.
    """
    if request.method in methods.items:
        return from_result(
            call(
                methods.items[request.method],
                extract_args(request, extra),
                extract_kwargs(request),
            ),
            request.id,
        )
    else:
        return MethodNotFoundResponse(request.method, request.id)


def dispatch_requests(
    methods: Methods, extra: Any, requests: Union[Request, List[Request]]
) -> Union[Response, List[Response]]:
    return (
        [dispatch_request(methods, extra, request) for request in requests]
        if isinstance(requests, list)
        else dispatch_request(methods, extra, cast(Request, requests))
    )


def create_requests(requests: Union[Dict, List[Dict]]) -> Union[Request, List[Request]]:
    """
    Maps a deserialized request(s) (i.e. dict or list) to Request(s).

    Args:
        requests: Request dict, or a list of dicts.

    Returns:
        A Request (or a list of them).
    """
    return (
        [Request(r["method"], r.get("params", []), r.get("id", NOID)) for r in requests]
        if isinstance(requests, list)
        else Request(
            requests["method"], requests.get("params", []), requests.get("id", NOID)
        )
    )


def validate(schema: dict, request: Union[Dict, List]) -> Union[Dict, List]:
    """
    Wraps jsonschema.validate, returning the same object passed in if
    successful.

    Raises an exception if invalid.

    Args:
        request: The deserialized-from-json request.
        schema: The jsonschema schema to validate against.

    Raises:
        jsonschema.ValidationError
    """
    validator.validate(request)
    return request


def dispatch_pure(
    methods: Methods, extra: Any, deserialize: Callable, schema: dict, request: str
) -> Union[Response, List[Response]]:
    """
    Dispatch a JSON-serialized request string to methods.

    Maps a request string to Response(s).

    Pure version of dispatch - no defaults, globals or logging. Use this
    function for testing, not dispatch.

    Args:
        methods: Collection of methods that can be called.
        extra: Will be included in the context dictionary passed to methods.
        deserialize: Function that is used to deserialize data.
        schema:
        request: The incoming request string.

    Returns:
        A Response.
    """
    try:
        try:
            deserialized = deserialize(request)
        except JSONDecodeError as exc:
            return ParseErrorResponse(str(exc))
        try:
            validate(deserialized, schema)
        except ValidationError as exc:
            return InvalidRequestResponse(str(exc))
        return dispatch_requests(methods, extra, create_requests(deserialized))
    except Exception as exc:
        logging.exception(exc)
        return ServerErrorResponse(str(exc), None)


@apply_config(config)
def dispatch(
    methods: Methods,
    request: str,
    *,
    extra: Optional[Any] = None,
    deserialize: Callable = default_deserialize,
) -> Union[Response, List[Response]]:
    """
    Dispatch a JSON-serialized request to methods.

    Maps a request string to Response(s).

    This is the main public method, which wraps dispatch_pure - adding default
    values, globals, logging.

    Args:
        methods: Collection of methods that can be called. If not passed, uses
            the internal methods object.
        request: The incoming request string.
        extra: Extra data available inside methods (as context.extra).
        deserialize: Function that is used to deserialize data.

    Returns:
        A Response.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', [ping])
    """
    try:
        request_logger.info(request)
        response = dispatch_pure(
            global_methods if methods is None else methods,
            extra,
            deserialize,
            global_schema,
            request,
        )
        if should_respond(response):
            response_logger.info(to_json(cast(Response, response)))
        return response
    except Exception as exc:
        logging.exception(exc)
        return ServerErrorResponse(str(exc), id=None)
