from configparser import ConfigParser
from typing import Any, Callable, Iterable, List, NamedTuple, Union
import json
import os
from functools import partial
from inspect import signature

from apply_defaults import apply_config  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pkg_resources import resource_string  # type: ignore
from oslash.either import Either, Left, Right  # type: ignore

from .exceptions import JsonRpcError
from .methods import Methods, global_methods
from .request import NOID, Request
from .response import (
    ErrorResponse,
    InvalidRequestResponse,
    ParseErrorResponse,
    Response,
    ServerErrorResponse,
    SuccessResponse,
    to_serializable,
)
from .result import (
    ErrorResult,
    InternalErrorResult,
    InvalidParamsResult,
    MethodNotFoundResult,
    Result,
    SuccessResult,
)

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

    Don't pass a notification to this function.
    """
    if dispatch_result.request.id is NOID:
        return Left(
            ServerErrorResponse(
                "Cannot respond to a notification", id=dispatch_result.request.id
            )
        )
    return (
        Left(
            ErrorResponse(
                **dispatch_result.result._error._asdict(), id=dispatch_result.request.id
            )
        )
        if isinstance(dispatch_result.result, Left)
        else Right(
            SuccessResponse(
                **dispatch_result.result._value._asdict(), id=dispatch_result.request.id
            )
        )
    )


def extract_args(request: Request, context: Any) -> list:
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context else params


def extract_kwargs(request: Request) -> dict:
    return request.params if isinstance(request.params, dict) else {}


def call(request: Request, context: Any, method: Callable) -> Result:
    try:
        result = method(*extract_args(request, context), **extract_kwargs(request))
        assert (
            isinstance(result, Left) and isinstance(result._error, ErrorResult)
        ) or (
            isinstance(result, Right) and isinstance(result._value, SuccessResult)
        ), f"The method did not return a valid Result"
        return result
    except JsonRpcError as exc:
        return Left(ErrorResult(code=exc.code, message=exc.message, data=exc.data))
    except Exception as exc:  # Other error inside method - Internal error
        # logging.exception(exc)
        return Left(InternalErrorResult(str(exc)))


def validate_args(
    request: Request,
    context: Any,
    func: Callable,
) -> Either[ErrorResult, Callable]:
    try:
        signature(func).bind(*extract_args(request, context), **extract_kwargs(request))
    except TypeError as exc:
        return Left(InvalidParamsResult(str(exc)))
    return Right(func)


def get_method(methods: Methods, method_name: str) -> Either[ErrorResult, Callable]:
    try:
        return Right(methods.items[method_name])
    except KeyError:
        return Left(MethodNotFoundResult(method_name))


def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> DispatchResult:
    return DispatchResult(
        request=request,
        result=get_method(methods, request.method)
        .bind(partial(validate_args, request, context))
        .bind(partial(call, request, context)),
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
            filter(
                lambda dr: dr.request.id is not NOID,
                map(
                    partial(dispatch_request, methods, context),
                    map(create_request, make_list(deserialized)),
                ),
            ),
        ),
    )


def validate(
    validator: Callable, request: Deserialized
) -> Either[ErrorResponse, Deserialized]:
    """We don't know which validator will be used, so the specific exception that will
    be raised is unknown. Any exception is an invalid request error.
    """
    try:
        validator(request)
    except Exception as exc:
        return Left(InvalidRequestResponse("The request failed schema validation"))
    return Right(request)


def deserialize(
    deserializer: Callable, request: str
) -> Either[ErrorResponse, Deserialized]:
    """We don't know which deserializer will be used, so the specific exception that
    will be raised is unknown. Any exception is a parse error.
    """
    try:
        return Right(deserializer(request))
    except Exception as exc:
        return Left(ParseErrorResponse(str(exc)))


def dispatch_to_response_pure(
    *,
    deserializer: Callable,
    schema_validator: Callable,
    methods: Methods,
    context: Any,
    request: str,
) -> Union[Response, Iterable[Response], None]:
    try:
        result = deserialize(deserializer, request).bind(
            partial(validate, schema_validator)
        )
        return (
            result
            if isinstance(result, Left)
            else dispatch_deserialized(methods, context, result._value)
        )
    except Exception as exc:
        return Left(ServerErrorResponse(str(exc), None))


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
