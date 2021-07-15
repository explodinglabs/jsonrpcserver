"""Asynchronous dispatch"""

from functools import partial
from typing import Any, Callable, Iterable, Union
import asyncio
import logging

from oslash.either import Left  # type: ignore

from .dispatcher import (
    Deserialized,
    DispatchResult,
    create_request,
    deserialize,
    extract_args,
    extract_kwargs,
    extract_list,
    get_method,
    make_list,
    to_response,
    validate_args,
    validate_request,
    validate_result,
)
from .exceptions import JsonRpcError
from .methods import Methods
from .request import Request, NOID
from .result import Result, InternalErrorResult, ErrorResult
from .response import Response, ServerErrorResponse
from .utils import compose


async def call(request: Request, context: Any, method: Callable) -> Result:
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
) -> DispatchResult:
    method = get_method(methods, request.method).bind(
        partial(validate_args, request, context)
    )
    return DispatchResult(
        request=request,
        result=(
            method
            if isinstance(method, Left)
            else await call(request, context, method._value)
        ),
    )


async def dispatch_deserialized(
    methods: Methods,
    context: Any,
    post_process: Callable,
    deserialized: Deserialized,
) -> Union[Response, Iterable[Response], None]:
    coroutines = (
        dispatch_request(methods, context, r)
        for r in map(create_request, make_list(deserialized))
    )
    results = await asyncio.gather(*coroutines)
    return extract_list(
        isinstance(deserialized, list),
        map(
            compose(post_process, to_response),
            filter(lambda dr: dr.request.id is not NOID, results),
        ),
    )


async def dispatch_to_response_pure(
    *,
    deserializer: Callable,
    schema_validator: Callable,
    methods: Methods,
    context: Any,
    post_process: Callable,
    request: str,
) -> Union[Response, Iterable[Response], None]:
    try:
        result = deserialize(deserializer, request).bind(
            partial(validate_request, schema_validator)
        )
        return (
            result
            if isinstance(result, Left)
            else await dispatch_deserialized(
                methods, context, post_process, result._value
            )
        )
    except Exception as exc:
        logging.exception(exc)
        return Left(ServerErrorResponse(str(exc), None))
