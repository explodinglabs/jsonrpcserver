"""Dispatcher - does the hard work of this library: parses, validates and dispatches
requests, providing responses.
"""

# pylint: disable=protected-access
import logging
from functools import partial
from inspect import signature
from itertools import starmap
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union

from returns.result import Failure, Result, Success

from .exceptions import JsonRpcError
from .methods import Method, Methods
from .request import Request
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
    SuccessResult,
)
from .sentinels import NOCONTEXT, NOID
from .utils import compose, make_list

ArgsValidator = Callable[[Any, Request, Method], Result[Method, ErrorResult]]
Deserialized = Union[Dict[str, Any], List[Dict[str, Any]]]

logger = logging.getLogger(__name__)


def extract_list(
    is_batch: bool, responses: Iterable[Response]
) -> Union[Response, List[Response], None]:
    """This is the inverse of make_list. Here we extract a response back out of the list
    if it wasn't a batch request originally. Also applies a JSON-RPC rule: we do not
    respond to batches of notifications.

    Args:
        is_batch: True if the original request was a batch.
        responses: Iterable of responses.

    Returns: A single response, a batch of responses, or None (returns None to a
        notification or batch of notifications, to indicate we should not respond).
    """
    # Need to materialize the iterable here to determine if it's empty. At least we're
    # at the end of processing (also need a list, not a generator, to serialize a batch
    # response with json.dumps).
    response_list = list(responses)
    # Responses have been removed, so in the case of either a single notification or a
    # batch of only notifications, return None
    if len(response_list) == 0:
        return None
    # For batches containing at least one non-notification, return the list
    if is_batch:
        return response_list
    # For single requests, extract it back from the list (there will be only one).
    return response_list[0]


def to_response(
    request: Request, result: Result[SuccessResult, ErrorResult]
) -> Response:
    """Maps a Request plus a Result to a Response. A Response is just a Result plus the
    id from the original Request.

    Raises: AssertionError if the request is a notification. Notifications can't be
        responded to. If a notification is given and AssertionError is raised, we should
        respond with Server Error, because notifications should have been removed by
        this stage.

    Returns: A Response.
    """
    assert request.id is not NOID
    return (
        Failure(ErrorResponse(**result.failure()._asdict(), id=request.id))
        if isinstance(result, Failure)
        else Success(SuccessResponse(**result.unwrap()._asdict(), id=request.id))
    )


def extract_args(request: Request, context: Any) -> List[Any]:
    """Extracts the positional arguments from the request.

    If a context object is given, it's added as the first argument.

    Returns: A list containing the positional arguments.
    """
    params = request.params if isinstance(request.params, list) else []
    return [context] + params if context is not NOCONTEXT else params


def extract_kwargs(request: Request) -> Dict[str, Any]:
    """Extracts the keyword arguments from the reqeust.

    Returns: A dict containing the keyword arguments.
    """
    return request.params if isinstance(request.params, dict) else {}


def validate_result(result: Result[SuccessResult, ErrorResult]) -> None:
    """Validate the return value from a method.

    Raises an AssertionError if the result returned from a method is invalid.

    Returns: None
    """
    assert (
        isinstance(result, Failure) and isinstance(result.failure(), ErrorResult)
    ) or (
        isinstance(result, Success) and isinstance(result.unwrap(), SuccessResult)
    ), f"The method did not return a valid Result (returned {result!r})"


def call(
    request: Request,
    context: Any,
    method: Method,
) -> Result[SuccessResult, ErrorResult]:
    """Call the method.

    Handles any exceptions raised in the method, being sure to return an Error response.

    Returns: A Result.
    """
    try:
        result = method(*extract_args(request, context), **extract_kwargs(request))
        # validate_result raises AssertionError if the return value is not a valid
        # Result, which should respond with Internal Error because its a problem in the
        # method.
        validate_result(result)
    # Raising JsonRpcError inside the method is an alternative way of returning an error
    # response.
    except JsonRpcError as exc:
        return Failure(ErrorResult(code=exc.code, message=exc.message, data=exc.data))
    # Any other uncaught exception inside method - internal error.
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception(exc)
        return Failure(InternalErrorResult(str(exc)))
    return result


def validate_args(
    request: Request,
    context: Any,
    func: Method,
) -> Result[Method, ErrorResult]:
    """Ensure the method can be called with the arguments given.

    Returns: Either the function to be called, or an Invalid Params error result.
    """
    try:
        signature(func).bind(*extract_args(request, context), **extract_kwargs(request))
    except TypeError as exc:
        return Failure(InvalidParamsResult(str(exc)))
    return Success(func)


def get_method(methods: Methods, method_name: str) -> Result[Method, ErrorResult]:
    """Get the requested method from the methods dict.

    Returns: Either the function to be called, or a Method Not Found result.
    """
    try:
        return Success(methods[method_name])
    except KeyError:
        return Failure(MethodNotFoundResult(method_name))


def dispatch_request(
    args_validator: ArgsValidator,
    methods: Methods,
    context: Any,
    request: Request,
) -> Tuple[Request, Result[SuccessResult, ErrorResult]]:
    """Get the method, validates the arguments and calls the method.

    Returns: A tuple containing the original Request, and the Result of the method call.
        We need the ids from the original request to remove notifications before
        responding, and  create a Response.
    """
    return (
        request,
        get_method(methods, request.method)
        .bind(partial(args_validator, request, context))
        .bind(partial(call, request, context)),
    )


def create_request(request: Dict[str, Any]) -> Request:
    """Create a Request namedtuple from a dict."""
    return Request(
        request["method"], request.get("params", []), request.get("id", NOID)
    )


def not_notification(request_result: Any) -> bool:
    """True if the request was not a notification.

    Used to filter out notifications from the list of responses.
    """
    return request_result[0].id is not NOID


def dispatch_deserialized(
    args_validator: ArgsValidator,
    post_process: Callable[[Response], Response],
    methods: Methods,
    context: Any,
    deserialized: Deserialized,
) -> Union[Response, List[Response], None]:
    """This is simply continuing the pipeline from dispatch_to_response_pure. It exists
    only to be an abstraction, otherwise that function is doing too much. It continues
    on from the request string having been parsed and validated.

    Returns: A Result, a list of Results, or None. If post_process is passed, it's
        applied to the Response(s).
    """
    results = map(
        compose(
            partial(dispatch_request, args_validator, methods, context), create_request
        ),
        make_list(deserialized),
    )
    responses = starmap(to_response, filter(not_notification, results))
    return extract_list(isinstance(deserialized, list), map(post_process, responses))


def validate_request(
    jsonrpc_validator: Callable[[Deserialized], Deserialized], request: Deserialized
) -> Result[Deserialized, ErrorResponse]:
    """Validate the request against a JSON-RPC schema.

    Ensures the parsed request is valid JSON-RPC.

    Returns: Either the same request passed in or an Invalid request response.
    """
    try:
        jsonrpc_validator(request)
    # Since the validator is unknown, the specific exception that will be raised is also
    # unknown. Any exception raised we assume the request is invalid and return an
    # "invalid request" response.
    except Exception:  # pylint: disable=broad-except
        return Failure(InvalidRequestResponse("The request failed schema validation"))
    return Success(request)


def deserialize_request(
    deserializer: Callable[[str], Deserialized], request: str
) -> Result[Deserialized, ErrorResponse]:
    """Parse the JSON request string.

    Returns: Either the deserialized request or a "Parse Error" response.
    """
    try:
        return Success(deserializer(request))
    # Since the deserializer is unknown, the specific exception that will be raised is
    # also unknown. Any exception raised we assume the request is invalid, return a
    # parse error response.
    except Exception as exc:  # pylint: disable=broad-except
        return Failure(ParseErrorResponse(str(exc)))


def dispatch_to_response_pure(
    args_validator: ArgsValidator,
    deserializer: Callable[[str], Deserialized],
    jsonrpc_validator: Callable[[Deserialized], Deserialized],
    post_process: Callable[[Response], Response],
    methods: Methods,
    context: Any,
    request: str,
) -> Union[Response, List[Response], None]:
    """A function from JSON-RPC request string to Response namedtuple(s), (yet to be
    serialized to json).

    Returns: A single Response, a list of Responses, or None. None is given for
        notifications or batches of notifications, to indicate that we should
        not respond.
    """
    try:
        result = deserialize_request(deserializer, request).bind(
            partial(validate_request, jsonrpc_validator)
        )
        return (
            post_process(result)
            if isinstance(result, Failure)
            else dispatch_deserialized(
                args_validator, post_process, methods, context, result.unwrap()
            )
        )
    except Exception as exc:  # pylint: disable=broad-except
        # There was an error with the jsonrpcserver library.
        logging.exception(exc)
        return post_process(Failure(ServerErrorResponse(str(exc), None)))
