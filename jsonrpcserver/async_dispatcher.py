"""Async version of dispatcher.py"""

from functools import partial
from itertools import starmap
from typing import Any, Callable, Iterable, Tuple, Union
import asyncio
import logging

from oslash.either import Left  # type: ignore

from .dispatcher import (
    Deserialized,
    create_request,
    deserialize_request,
    extract_args,
    extract_kwargs,
    extract_list,
    get_method,
    not_notification,
    to_response,
    validate_args,
    validate_request,
    validate_result,
)
from .exceptions import JsonRpcError
from .methods import Method, Methods
from .request import Request
from .result import Result, InternalErrorResult, ErrorResult
from .response import Response, ServerErrorResponse
from .utils import make_list


async def call(request: Request, context: Any, method: Method) -> Result:
    try:
        result = await method(
            *extract_args(request, context), **extract_kwargs(request)
        )
        validate_result(result)
    except JsonRpcError as exc:
        return Left(ErrorResult(code=exc.code, message=exc.message, data=exc.data))
    except Exception as exc:  # Other error inside method - Internal error
        logging.exception(exc)
        return Left(InternalErrorResult(str(exc)))
    return result


async def dispatch_request(
    methods: Methods, context: Any, request: Request
) -> Tuple[Request, Result]:
    method = get_method(methods, request.method).bind(
        partial(validate_args, request, context)
    )
    return (
        request,
        method
        if isinstance(method, Left)
        else await call(request, context, method._value),
    )


async def dispatch_deserialized(
    methods: Methods,
    context: Any,
    post_process: Callable[[Response], Iterable[Any]],
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
    post_process: Callable[[Response], Iterable[Any]],
    request: str,
) -> Union[Response, Iterable[Response], None]:
    try:
        result = deserialize_request(deserializer, request).bind(
            partial(validate_request, validator)
        )
        return (
            post_process(result)
            if isinstance(result, Left)
            else await dispatch_deserialized(
                methods, context, post_process, result._value
            )
        )
    except Exception as exc:
        logging.exception(exc)
        return post_process(Left(ServerErrorResponse(str(exc), None)))
