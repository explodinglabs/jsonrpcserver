"""Async version of dispatcher.py"""

import asyncio
import logging
from functools import partial
from inspect import signature
from itertools import starmap
from typing import Any, Callable, Iterable, Tuple, Union

from returns.result import Failure, Result, Success

from .async_methods import Method, Methods
from .dispatcher import (
    Deserialized,
    create_request,
    deserialize_request,
    extract_args,
    extract_kwargs,
    extract_list,
    not_notification,
    to_response,
    validate_request,
    validate_result,
)
from .exceptions import JsonRpcError
from .request import Request
from .response import Response, ServerErrorResponse
from .result import (
    ErrorResult,
    InternalErrorResult,
    InvalidParamsResult,
    MethodNotFoundResult,
    SuccessResult,
)
from .utils import make_list

logger = logging.getLogger(__name__)


async def call(
    request: Request, context: Any, method: Method
) -> Result[SuccessResult, ErrorResult]:
    try:
        result = await method(
            *extract_args(request, context), **extract_kwargs(request)
        )
        validate_result(result)
    except JsonRpcError as exc:
        return Failure(ErrorResult(code=exc.code, message=exc.message, data=exc.data))
    except Exception as exc:
        # Other error inside method - Internal error
        logger.exception(exc)
        return Failure(InternalErrorResult(str(exc)))
    return result


def validate_args(
    request: Request, context: Any, func: Method
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


async def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> Tuple[Request, Result[SuccessResult, ErrorResult]]:
    method = get_method(methods, request.method).bind(
        partial(validate_args, request, context)
    )
    return (
        request,
        method
        if isinstance(method, Failure)
        else await call(request, context, method.unwrap()),
    )


async def dispatch_deserialized(
    methods: Methods,
    context: Any,
    post_process: Callable[[Response], Response],
    deserialized: Deserialized,
) -> Union[Response, Iterable[Response], None]:
    results = await asyncio.gather(
        *(
            dispatch_request(methods, context, r)
            for r in map(create_request, make_list(deserialized))
        )
    )
    return extract_list(
        isinstance(deserialized, list),
        map(
            post_process,
            starmap(to_response, filter(not_notification, results)),
        ),
    )


async def dispatch_to_response_pure(
    *,
    deserializer: Callable[[str], Deserialized],
    validator: Callable[[Deserialized], Deserialized],
    methods: Methods,
    context: Any,
    post_process: Callable[[Response], Response],
    request: str,
) -> Union[Response, Iterable[Response], None]:
    try:
        result = deserialize_request(deserializer, request).bind(
            partial(validate_request, validator)
        )
        return (
            post_process(result)
            if isinstance(result, Failure)
            else await dispatch_deserialized(
                methods,
                context,
                post_process,
                result.unwrap(),
            )
        )
    except Exception as exc:
        logger.exception(exc)
        return post_process(Failure(ServerErrorResponse(str(exc), None)))
