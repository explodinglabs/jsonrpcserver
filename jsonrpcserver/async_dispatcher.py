"""Asynchronous dispatch"""

import asyncio
import collections.abc
import logging
from json import JSONDecodeError
from json import loads as default_deserialize
from typing import Any, Iterable, Optional, Union, Callable

from apply_defaults import apply_config  # type: ignore
from jsonschema import ValidationError  # type: ignore

from .dispatcher import (
    config,
    create_requests,
    global_schema,
    validate,
)
from .methods import Methods, global_methods, validate_args
from .request import Request, is_notification
from .response import Response
from .result import InvalidParams, InternalError, Result


async def call(request, method, *args, **kwargs) -> Result:
    errors = validate_args(method, *args, **kwargs)
    if errors:
        return InvalidParams(errors)

    try:
        return await method(*args, **kwargs)
    except Exception as exc:  # Other error inside method - server error
        logging.exception(exc)
        return InternalError(str(exc))


async def safe_call(
    request: Request, methods: Methods, *, extra: Any, serialize: Callable
) -> Response:
    try:
        result = (
            await call(
                methods.items[request.method],
                *([Context(request=request, extra=extra)] + request.params),
            )
            if isinstance(request.params, list)
            else await call(
                methods.items[request.method],
                Context(request=request, extra=extra),
                **request.params,
            )
        )
        # Ensure value returned from the method is JSON-serializable. If not,
        # handle_exception will set handler.response to an ExceptionResponse
        serialize(result)
    except asyncio.CancelledError:
        # Allow CancelledError from asyncio task cancellation to bubble up. Without
        # this, CancelledError is caught and handled, resulting in a "Server error"
        # response object from the dispatcher, but because the CancelledError doesn't
        # bubble up the rpc_server task doesn't exit. See PR
        # https://github.com/bcb/jsonrpcserver/pull/132
        raise
    except Exception as exc:  # Other error inside method - server error
        logging.exception(exc)
        return ExceptionResponse(exc, id=request.id)
    else:
        return (
            NotificationResponse()
            if is_notification(request)
            else SuccessResponse(result=result, id=request.id, serialize_func=serialize)
        )


async def dispatch_requests(
    requests: Union[Request, Iterable[Request]],
    methods: Methods,
    extra: Any,
    serialize: Callable,
) -> Response:
    if isinstance(requests, collections.abc.Iterable):
        responses = (
            safe_call(r, methods, extra=extra, serialize=serialize) for r in requests
        )
        return BatchResponse(await asyncio.gather(*responses), serialize_func=serialize)
    return await safe_call(requests, methods, extra=extra, serialize=serialize)


async def dispatch_pure(
    request: str,
    methods: Methods,
    *,
    extra: Any,
    serialize: Callable,
    deserialize: Callable,
) -> Response:
    try:
        deserialized = validate(deserialize(request), global_schema)
    except JSONDecodeError as exc:
        return InvalidJSONResponse(data=str(exc))
    except ValidationError as exc:
        return InvalidJSONRPCResponse(data=None)
    return await dispatch_requests(
        create_requests(deserialized),
        methods,
        extra=extra,
        serialize=serialize,
    )


@apply_config(config)
async def dispatch(
    request: str,
    methods: Optional[Methods] = None,
    *,
    extra: Optional[Any] = None,
    deserialize: Callable = default_deserialize,
    **kwargs: Any,
) -> Response:
    # Use the global methods object if no methods object was passed.
    methods = global_methods if methods is None else methods
    # Add temporary stream handlers for this request, and remove them later
    logger.info(request)
    response = await dispatch_pure(
        request,
        methods,
        extra=extra,
        serialize=serialize,
        deserialize=deserialize,
    )
    logger.info(to_json(response))
    # Remove the temporary stream handlers
    if basic_logging:
        remove_handlers(request_handler, response_handler)
    return response
