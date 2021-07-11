from configparser import ConfigParser
from typing import Any, Callable, Iterable, List, NamedTuple, Union
import json
import os
from inspect import signature
from itertools import filterfalse

from apply_defaults import apply_config  # type: ignore
from pkg_resources import resource_string  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pymonad.tools import curry  # type: ignore

from .exceptions import JsonRpcError
from .methods import Methods, global_methods
from .request import NOID, Request, is_notification
from .response import (
    ErrorResponse,
    InvalidRequestResponse,
    ParseErrorResponse,
    Response,
    SuccessResponse,
    to_serializable,
)
from .result import Error, InternalError, InvalidParams, MethodNotFound, Result, Success

Deserialized = Union[dict, List[dict]]
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


def validate_result(result: Result) -> Result:
    """Ensure value returned from method is a Result."""
    return (
        result
        if isinstance(result, (Success, Error))
        else InternalError("The method did not return a Result")
    )


def call(method: Callable, args: list, kwargs: dict) -> Result:
    try:
        return method(*args, **kwargs)
    except JsonRpcError as exc:
        return Error(code=exc.code, message=exc.message, data=exc.data)
    except Exception as exc:  # Other error inside method - Internal error
        # logging.exception(exc)
        return InternalError(str(exc))


def extract_args(request: Request, context: Any) -> list:
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context else params


def extract_kwargs(request: Request) -> dict:
    return request.params if isinstance(request.params, dict) else {}


def validate_args(func: Callable, *args: Any, **kwargs: Any) -> Result:
    try:
        signature(func).bind(*args, **kwargs)
    except TypeError as exc:
        return InvalidParams(str(exc))
    return Success(func)


@curry(2)
def get_method(methods: Methods, method_name: str) -> Either[Error, Callable]:
    try:
        return Success(methods.items[method_name])
    except KeyError:
        return MethodNotFound(method_name)


@curry(3)
def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> DispatchResult:
    # *extract_args(request, context), **extract_kwargs(request)
    return DispatchResult(
        request=request,
        result=(
            Success(request.method)
            .bind(get_method(methods))
            .bind(validate_args(request, context))
            .bind(call(request, context))
            .bind(validate_result)
        ),
    )


def extract_list(
    is_batch: bool, responses: Iterable[Response]
) -> Union[Response, List[Response], None]:
    """If it's a batch request, extract a single request from the list.

    We also apply a JSON-RPC rule here. If it's a notification, or a batch of all
    notifications, we should not respond. That means returning None instead of an empty
    list.
    """
    # We have to reify the list here to determine if it's empty, which is unfortunate
    # because we do another map later (when serializing to dicts). This function doesn't
    # use the Responses, though, it could be an iterable of anything. So we could
    # serialize before reaching here.
    response_list = list(responses)
    return (
        None
        if len(response_list) == 0
        else (
            response_list if is_batch else response_list[0]
        )  # There will be at lease one request in a valid batch request
    )


def to_response(dispatch_result: DispatchResult) -> Response:
    """Maps DispatchResults to Responses.

    Don't pass a notification (filter them out before calling)."""
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


def create_request(request: dict) -> Request:
    return Request(
        request["method"], request.get("params", []), request.get("id", NOID)
    )


def make_list(x: Any) -> list:
    return [x] if not isinstance(x, list) else x


def dispatch_deserialized(
    methods: Methods, context: Any, deserialized: Deserialized
) -> Union[Response, Iterable[Response], None]:
    return extract_list(
        isinstance(deserialized, list),
        map(
            to_response,
            filterfalse(
                is_notification,
                map(
                    dispatch_request(methods, context),
                    map(create_request, make_list(deserialized)),
                ),
            ),
        ),
    )


@curry(2)
def validate(validator: Callable, request: Deserialized) -> Either[Error, Deserialized]:
    """We don't know which validator will be used, so the specific exception that will
    be raised is unknown. Any exception is an invalid request error.
    """
    try:
        validator(request)
    except Exception as exc:
        return InvalidRequestResponse("The request failed schema validation")
    return Success(request)


@curry(2)
def deserialize(deserializer: Callable, request: str) -> Either[Error, Deserialized]:
    """We don't know which deserializer will be used, so the specific exception that
    will be raised is unknown. Any exception is a parse error.
    """
    try:
        return Success(deserializer(request))
    except Exception as exc:
        return ParseErrorResponse(str(exc))


def dispatch_to_response_pure(
    *,
    deserializer: Callable,
    schema_validator: Callable,
    methods: Methods,
    context: Any,
    request: str,
) -> Union[Response, Iterable[Response], None]:
    result = (
        Success(request)
        .bind(deserialize(deserializer))
        .bind(validate(schema_validator))
    )
    return (
        result
        if result.is_left()
        else dispatch_deserialized(methods, context, result._value)
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
