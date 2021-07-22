from functools import partial
from inspect import signature
from itertools import starmap
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union
import logging

from oslash.either import Either, Left, Right  # type: ignore

from .exceptions import JsonRpcError
from .methods import Method, Methods
from .request import NOID, Request
from .response import (
    ErrorResponse,
    InvalidRequestResponse,
    ParseErrorResponse,
    Response,
    ServerErrorResponse,
    SuccessResponse,
)
from .result import (
    ErrorResult,
    InternalErrorResult,
    InvalidParamsResult,
    MethodNotFoundResult,
    Result,
    SuccessResult,
)
from .utils import compose, make_list


Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]


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


def to_response(request: Request, result: Result) -> Response:
    """Maps Requests & Results to Responses."""
    # Don't pass a notification to this function - should return a Server Error.
    assert request.id is not NOID
    return (
        Left(ErrorResponse(**result._error._asdict(), id=request.id))
        if isinstance(result, Left)
        else Right(SuccessResponse(**result._value._asdict(), id=request.id))
    )


def extract_args(request: Request, context: Any) -> List[Any]:
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context else params


def extract_kwargs(request: Request) -> Dict[str, Any]:
    return request.params if isinstance(request.params, dict) else {}


def validate_result(result: Result) -> None:
    assert (isinstance(result, Left) and isinstance(result._error, ErrorResult)) or (
        isinstance(result, Right) and isinstance(result._value, SuccessResult)
    ), f"The method did not return a valid Result (returned {result!r})"


def call(request: Request, context: Any, method: Method) -> Result:
    try:
        result = method(*extract_args(request, context), **extract_kwargs(request))
        # The method should return a valid Result, else respond with "internal error".
        validate_result(result)
    except JsonRpcError as exc:
        return Left(ErrorResult(code=exc.code, message=exc.message, data=exc.data))
    except Exception as exc:  # Other error inside method - Internal error
        logging.exception(exc)
        return Left(InternalErrorResult(str(exc)))
    return result


def validate_args(
    request: Request, context: Any, func: Method
) -> Either[ErrorResult, Method]:
    try:
        signature(func).bind(*extract_args(request, context), **extract_kwargs(request))
    except TypeError as exc:
        return Left(InvalidParamsResult(str(exc)))
    return Right(func)


def get_method(methods: Methods, method_name: str) -> Either[ErrorResult, Method]:
    try:
        return Right(methods.items[method_name])
    except KeyError:
        return Left(MethodNotFoundResult(method_name))


def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> Tuple[Request, Result]:
    return (
        request,
        get_method(methods, request.method)
        .bind(partial(validate_args, request, context))
        .bind(partial(call, request, context)),
    )


def create_request(request: Dict[str, Any]) -> Request:
    return Request(
        request["method"], request.get("params", []), request.get("id", NOID)
    )


def not_notification(request_result: Any) -> bool:
    return request_result[0].id is not NOID


def dispatch_deserialized(
    methods: Methods,
    context: Any,
    post_process: Callable[[Response], Iterable[Any]],
    deserialized: Deserialized,
) -> Union[Response, Iterable[Response], None]:
    results = map(
        compose(partial(dispatch_request, methods, context), create_request),
        make_list(deserialized),
    )
    return extract_list(
        isinstance(deserialized, list),
        map(
            post_process,
            starmap(to_response, filter(not_notification, results)),
        ),
    )


def validate_request(
    validator: Callable[[Deserialized], Deserialized], request: Deserialized
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
    deserializer: Callable[[str], Deserialized], request: str
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
    deserializer: Callable[[str], Deserialized],
    schema_validator: Callable[[Deserialized], Deserialized],
    methods: Methods,
    context: Any,
    post_process: Callable[[Response], Iterable[Any]],
    request: str,
) -> Union[Response, Iterable[Response], None]:
    try:
        result = deserialize(deserializer, request).bind(
            partial(validate_request, schema_validator)
        )
        return (
            result
            if isinstance(result, Left)
            else dispatch_deserialized(methods, context, post_process, result._value)
        )
    except Exception as exc:
        # An error with the jsonrpcserver library.
        logging.exception(exc)
        return Left(ServerErrorResponse(str(exc), None))
