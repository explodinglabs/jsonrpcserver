"""
Dispatcher.

The dispatch() function takes a JSON-RPC request, calls the appropriate method, then
returns the response.
"""
import json
import os
import logging
from configparser import ConfigParser
from typing import Any, Callable, Dict, List, Union

from apply_defaults import apply_config  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pkg_resources import resource_string  # type: ignore

from .methods import Methods, global_methods, validate_args
from .request import Request, NOID
from .response import (
    InvalidRequestResponse,
    MethodNotFoundResponse,
    ParseErrorResponse,
    Response,
    ServerErrorResponse,
    from_result,
    to_serializable,
)
from .result import InvalidParams, InternalError, Result

default_deserializer = json.loads

# Prepare the jsonschema validator. This is global so it loads only once, not every
# time dispatch is called.
schema = json.loads(resource_string(__name__, "request-schema.json"))
klass = validator_for(schema)
klass.check_schema(schema)
default_schema_validator = klass(schema).validate

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


def extract_args(request: Request, context: Any) -> list:
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context else params


def extract_kwargs(request: Request) -> dict:
    return request.params if isinstance(request.params, dict) else {}


def dispatch_request(
    *, methods: Methods, context: Any, request: Request
) -> Union[Response, None]:
    """
    Dispatch a single Request.

    Maps a single Request to a single Response.

    Converts the return value (a Result) into a Response.
    """
    if request.method in methods.items:
        result = call(
            methods.items[request.method],
            extract_args(request, context),
            extract_kwargs(request),
        )
        return None if request.id is NOID else from_result(result, request.id)
    else:
        return MethodNotFoundResponse(request.method, request.id)


def none_if_empty(x: Any) -> Any:
    return None if not x else x


def remove_nones(responses: List[Union[None, Response]]) -> Union[List[Response]]:
    return [x for x in responses if x is not None]


def dispatch_requests(
    *, methods: Methods, context: Any, requests: Union[Request, List[Request]]
) -> Union[None, Response, List[Response]]:
    """Important: The methods must be called. If all requests are notifications."""
    return (
        # Nones (notifications) must be removed - "A Response object SHOULD exist for
        # each Request object, except that there SHOULD NOT be any Response objects for
        # notifications."
        # Also should not return an empty list, "If there are no Response objects
        # contained within the Response array as it is to be sent to the client, the
        # server MUST NOT return an empty Array and should return nothing at all."
        none_if_empty(
            remove_nones(
                [
                    dispatch_request(methods=methods, context=context, request=r)
                    for r in requests
                ]
            )
        )
        if isinstance(requests, list)
        else dispatch_request(methods=methods, context=context, request=requests)
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


def validate(validator: Callable, request: Union[Dict, List]) -> Union[Dict, List]:
    """
    Wraps jsonschema.validate, returning the same object passed in if successful.

    Raises an exception if invalid.

    Args:
        request: The deserialized-from-json request.

    Returns:
        The same object passed in.

    Raises:
        An exception,
    """
    validator(request)
    return request


def dispatch_to_response_pure(
    *,
    methods: Methods,
    context: Any,
    schema_validator: Callable,
    deserializer: Callable,
    request: str,
) -> Union[Response, List[Response], None]:
    """
    Dispatch a JSON-serialized request string to methods.

    Maps a request string to Response(s).

    Pure version of dispatch - no defaults, globals, or logging. Use this function for
    testing, not dispatch_to_response or dispatch.

    Args:
        methods: Collection of methods that can be called.
        context: Will be passed to methods as the first param if not None.
        deserialize: Function that is used to deserialize data.
        request: The incoming request string.

    Returns:
        A Response, list of Responses, or None if all requests were notifications.
    """
    try:
        try:
            deserialized = deserializer(request)
        # We don't know which deserializer will be used, so the specific exception that
        # will be raised is unknown. Any exception is a parse error.
        except Exception as exc:
            return ParseErrorResponse(str(exc))
        # As above, we don't know which validator will be used, so the specific
        # exception that will be raised is unknown. Any exception is an invalid request
        # error.
        try:
            schema_validator(deserialized)
        except Exception as exc:
            return InvalidRequestResponse("The request failed schema validation")
        return dispatch_requests(
            methods=methods, context=context, requests=create_requests(deserialized)
        )
    except Exception as exc:
        logging.exception(exc)
        return ServerErrorResponse(str(exc), None)


@apply_config(config)
def dispatch_to_response(
    request: str,
    methods: Methods = None,
    *,
    context: Any = None,
    schema_validator: Callable = default_schema_validator,
    deserializer: Callable = default_deserializer,
) -> Union[Response, List[Response], None]:
    """
    Dispatch a JSON-serialized request to methods.

    Maps a request string to a Response (or list of Responses).

    This is a public method which wraps dispatch_to_response_pure, adding default values
    and globals.

    Args:
        request: The JSON-RPC request string.
        methods: Collection of methods that can be called. If not passed, uses the
            internal methods object.
        context: Will be passed to methods as the first param if not None.
        schema_validator:
        deserialize: Function that is used to deserialize data.
        request: The incoming request string.

    Returns:
        A Response, list of Responses or None.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', [ping])
    """
    return dispatch_to_response_pure(
        methods=global_methods if methods is None else methods,
        context=context,
        schema_validator=schema_validator,
        deserializer=deserializer,
        request=request,
    )


def dispatch_to_json(
    *args: Any,
    serializer: Callable = json.dumps,
    **kwargs: Any,
) -> str:
    """
    This is the main public method, it goes through the entire JSON-RPC process
    - taking a JSON-RPC request string, dispatching it, converting the Response(s) into
    a serializable value and then serializing that to return a JSON-RPC response
    string.
    """
    return serializer(to_serializable(dispatch_to_response(*args, **kwargs)))


# "dispatch" is an alias of dispatch_to_json.
dispatch = dispatch_to_json
