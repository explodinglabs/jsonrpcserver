"""
Dispatcher.

The dispatch function takes a JSON-RPC request, logs it, calls the appropriate method,
then logs and returns the response.
"""
import logging
from json import dumps as serialize, loads as deserialize, JSONDecodeError
from typing import Any, Dict, Optional, List, Union, cast
from pkg_resources import resource_string

from jsonschema import validate as validate_jsonrpc, ValidationError  # type: ignore

from . import methods as global_methods
from .log import log_
from .methods import Methods, validate_args
from .request import Request, UNSPECIFIED
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


def validate(deserialized):
    validate_jsonrpc(deserialized, schema)
    return deserialized


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
        # Return the result in a SuccessResponse (or NotificationResponse)
        return (
            NotificationResponse()
            if request.is_notification
            else SuccessResponse(result=result, id=request.id)
        )
    except KeyError:  # Method not found
        return MethodNotFoundResponse(id=request.id, debug=debug)
    except TypeError as exc:  # Validate args failed
        return InvalidParamsResponse(request.method, data=str(exc), debug=debug)
    except Exception as exc:  # Other error inside method - server error
        return ExceptionResponse(exc, id=request.id, debug=debug)


def dispatch_deserialized(
    requests: Union[Dict, List],
    methods: Methods,
    *,
    debug: bool,
    context: Any = UNSPECIFIED,
    convert_camel_case: Optional[bool] = False,
):
    """
    Takes deserialized object (dict or list of dicts), which is valid jsonrpc.
    """
    if isinstance(requests, list):
        return BatchResponse(
            dispatch_request(Request(**request, context=context), methods, debug=debug)
            for request in requests
        )
    # Single request
    return dispatch_request(
        Request(**requests, context=context), methods, debug=debug
    )


# @apply_config(config)
def dispatch_pure(
    requests: str, methods: Methods, *, debug: bool, **kwargs: Any
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
            validate(deserialize(requests)), methods, debug=debug, **kwargs
        )
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc), debug=debug)
    except ValidationError as exc:
        return InvalidJSONRPCResponse(data=str(exc), debug=debug)


def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    trim_log_values: bool = False,
    **kwargs: Any,
) -> Response:
    """
    Dispatch a request (or requests) to methods.

    This is the main public method.

    Args:
        trim_log_values: Show abbreviated requests and responses in log.

    Returns:
        A Response.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', methods)
    """
    methods = global_methods if methods is None else methods
    log_request(request, trim_log_values=trim_log_values)
    response = dispatch_pure(request, methods, **kwargs)
    log_response(response, trim_log_values=trim_log_values)
    return response
