from configparser import ConfigParser
from typing import Any, Callable, Iterable, NamedTuple, Union
import json
import logging
import os

from apply_defaults import apply_config  # type: ignore
from pkg_resources import resource_string  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pymonad.tools import curry, identity  # type: ignore
from pymonad.either import Either, Left, Right  # type: ignore

from .exceptions import JsonRpcError
from .methods import Methods, global_methods, validate_args
from .request import Request, NOID
from .response import (
    ErrorResponse,
    InvalidRequestResponse,
    ParseErrorResponse,
    Response,
    SuccessResponse,
    to_serializable,
)
from .result import Error, InternalError, InvalidParams, MethodNotFound, Result, Success


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


class DispatchResult(NamedTuple):
    request: Request
    result: Result


def extract_args(request: Request, context: Any) -> list:
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context else params


def extract_kwargs(request: Request) -> dict:
    return request.params if isinstance(request.params, dict) else {}


def from_result(dispatch_result: DispatchResult) -> Response:
    """Converts a Result to a Response (by adding the request id)."""
    assert dispatch_result.request.id is not NOID, "Can't respond to a notification"
    return (
        SuccessResponse(
            **dispatch_result.result._asdict(), id=dispatch_result.request.id
        )
        if isinstance(dispatch_result.result, Success)
        else ErrorResponse(
            **dispatch_result.result._asdict(), id=dispatch_result.request.id
        )
    )


def from_results(
    dispatch_results: Iterable[DispatchResult], is_batch: bool
) -> Union[Response, Iterable[Response], None]:
    # Gather the responses (only for the non-notifications).
    responses = list(
        map(from_result, filter(lambda dr: dr.request.id is not NOID, dispatch_results))
    )
    # Two rules need to be applied here: we should not respond to a list of
    # notifications, that means returning None. Secondly, if it's not a batch request,
    # take a single response out of the list.
    return None if not len(responses) else (responses if is_batch else responses[0])


def call(methods: Methods, method_name: str, args: list, kwargs: dict) -> Result:
    """
    Calls a method.

    Catches exceptions to ensure we always return a Response.

    Returns:
        The Result from the method call.
    """
    try:
        method = methods.items[method_name]
    except KeyError:
        return MethodNotFound(method_name)

    errors = validate_args(method, *args, **kwargs)
    if errors:
        return InvalidParams(errors)

    try:
        result = method(*args, **kwargs)
    except JsonRpcError as exc:
        return Error(code=exc.code, message=exc.message, data=exc.data)
    except Exception as exc:  # Other error inside method - server error
        logging.exception(exc)
        return InternalError(str(exc))
    else:
        return (
            InternalError("The method did not return a Result")
            if not isinstance(result, (Success, Error))
            else result
        )


@curry(3)
def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> DispatchResult:
    return DispatchResult(
        request=request,
        result=call(
            methods,
            request.method,
            extract_args(request, context),
            extract_kwargs(request),
        ),
    )


def create_request(request: dict) -> Request:
    return Request(
        request["method"], request.get("params", []), request.get("id", NOID)
    )


def make_list(x: Any) -> list:
    return [x] if not isinstance(x, list) else x


@curry(2)
def validate(
    validator: Callable, request: Union[dict, list]
) -> Either[Union[dict, list], Response]:
    """
    We don't know which validator will be used, so the specific exception that will be
    raised is unknown. Any exception is an invalid request error.
    """
    try:
        validator(request)
    except Exception as exc:
        return Left(InvalidRequestResponse("The request failed schema validation"))
    return Right(request)


@curry(2)
def deserialize(
    deserializer: Callable, request: str
) -> Either[Union[dict, list], Response]:
    """
    We don't know which deserializer will be used, so the specific exception that will
    be raised is unknown. Any exception is a parse error.
    """
    try:
        return Right(deserializer(request))
    except Exception as exc:
        return Left(ParseErrorResponse(str(exc)))


def dispatch_to_response_pure(
    *,
    deserializer: Callable,
    schema_validator: Callable,
    context: Any,
    methods: Methods,
    request: str,
) -> Union[Response, Iterable[Response], None]:
    return (
        Right(request)
        .bind(deserialize(deserializer))
        .bind(validate(schema_validator))
        .either(
            identity,
            lambda deserialized: from_results(
                map(
                    dispatch_request(methods, context),
                    map(create_request, make_list(deserialized)),
                ),
                isinstance(deserialized, list),
            ),
        )
    )


# --------------------------------------------------------------------------------------
# Above here is pure: no using globals, default values, or raising exceptions. (actually
# catching exceptions is impure but there's no escaping it.)
#
# Below is the public developer API.
# --------------------------------------------------------------------------------------


@apply_config(config)
def dispatch_to_response(
    request: str,
    methods: Methods = None,
    *,
    context: Any = None,
    schema_validator: Callable = default_schema_validator,
    deserializer: Callable = default_deserializer,
) -> Union[Response, Iterable[Response], None]:
    """
    Dispatch a JSON-serialized request to methods.

    Maps a request string to a Response (or list of Responses).

    This is a public method which wraps dispatch_to_response_pure, adding default values
    and globals.

    Args:
        request: The JSON-RPC request string.
        methods: Collection of methods that can be called. If not passed, uses the
            internal, global methods object which is populated with the @method
            decorator.
        context: Will be passed to methods as the first param if not None.
        schema_validator: Function that validates the JSON-RPC request.
        deserializer: Function that deserializes the JSON-RPC request.

    Returns:
        A Response, list of Responses or None.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', [ping])
    """
    return dispatch_to_response_pure(
        deserializer=deserializer,
        schema_validator=schema_validator,
        context=context,
        methods=global_methods if methods is None else methods,
        request=request,
    )


def dispatch_to_serializable(*args: Any, **kwargs: Any) -> Union[dict, list, None]:
    return to_serializable(dispatch_to_response(*args, **kwargs))


def dispatch_to_json(
    *args: Any, serializer: Callable = json.dumps, **kwargs: Any
) -> str:
    """
    This is the main public method, it goes through the entire JSON-RPC process
    - taking a JSON-RPC request string, dispatching it, converting the Response(s) into
    a serializable value and then serializing that to return a JSON-RPC response
    string.
    """
    return serializer(dispatch_to_serializable(*args, **kwargs))


# "dispatch" is an alias of dispatch_to_json.
dispatch = dispatch_to_json
