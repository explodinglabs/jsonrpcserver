# type: ignore
"""Asynchronous dispatch"""

import asyncio
import logging

from apply_defaults import apply_config  # type: ignore

from .dispatcher import config
from .methods import Methods, global_methods, validate_args
from .request import Request
from .response import Response
from .result import InvalidParams, InternalError, Result


async def call(methods: Methods, method_name: str, args: list, kwargs: dict) -> Result:
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
    except asyncio.CancelledError:
        # Allow CancelledError from asyncio task cancellation to bubble up. Without
        # this, CancelledError is caught and handled, resulting in a "Server error"
        # response object from the dispatcher, but because the CancelledError doesn't
        # bubble up the rpc_server task doesn't exit. See PR
        # https://github.com/bcb/jsonrpcserver/pull/132
        raise
    except Exception as exc:  # Other error inside method - server error
        logging.exception(exc)
        return InternalError(str(exc))
    else:
        return (
            InternalError("The method did not return a Result")
            if not isinstance(result, (Success, Error))
            else result
        )


def dispatch_request(
    *, methods: Methods, context: Any, request: Request
) -> Union[Response, None]:
    """
    Dispatch a single Request.

    Maps a single Request to a single Response.

    Converts the return value (a Result) into a Response.
    """
    result = await call(
        methods,
        request.method,
        extract_args(request, context),
        extract_kwargs(request),
    )
    return None if request.id is NOID else from_result(result, request.id)


async def dispatch_requests(
    *, methods: Methods, context: Any, requests: Union[Request, List[Request]]
) -> Union[None, Response, List[Response]]:
    """Important: The methods must be called. If all requests are notifications."""
    return (
        # Nones (notifications) must be removed - "A Response object SHOULD exist for
        # each Request object, except that there SHOULD NOT be any Response objects for
        # notifications."
        # Also should not return an empty list, "If there are no Response objects
        # contained within the Response array as it is to be sent to the client, the
        # server MUST NOT return an empty Array and should return nothing at all."
        none_if_empty(
            remove_nones(
                [
                    await dispatch_request(methods=methods, context=context, request=r)
                    for r in requests
                ]
            )
        )
        if isinstance(requests, list)
        else await dispatch_request(methods=methods, context=context, request=requests)
    )


@apply_config(config)
async def dispatch_to_response_pure(
    *,
    deserializer: Callable,
    schema_validator: Callable,
    context: Any,
    methods: Methods,
    request: str,
) -> Union[Response, List[Response], None]:
    try:
        try:
            deserialized = deserializer(request)
        # We don't know which deserializer will be used, so the specific exception that
        # will be raised is unknown. Any exception is a parse error.
        except Exception as exc:
            return ParseErrorResponse(str(exc))
        # As above, we don't know which validator will be used, so the specific
        # exception that will be raised is unknown. Any exception is an invalid request
        # error.
        try:
            schema_validator(deserialized)
        except Exception as exc:
            return InvalidRequestResponse("The request failed schema validation")
        return await dispatch_requests(
            methods=methods, context=context, requests=create_requests(deserialized)
        )
    except Exception as exc:
        logging.exception(exc)
        return ServerErrorResponse(str(exc), None)


# --------------------------------------------------------------------------------------
# Above here is pure: no using globals, default values, or raising exceptions. (actually
# catching exceptions is impure but there's no escaping it.)
#
# Below is the public developer API.
# --------------------------------------------------------------------------------------


@apply_config(config)
async def dispatch_to_response(
    request: str,
    methods: Methods = None,
    *,
    context: Any = None,
    schema_validator: Callable = default_schema_validator,
    deserializer: Callable = default_deserializer,
) -> Union[Response, List[Response], None]:
    return await dispatch_to_response_pure(
        deserializer=deserializer,
        schema_validator=schema_validator,
        context=context,
        methods=global_methods if methods is None else methods,
        request=request,
    )


async def dispatch_to_serializable(*args: Any, **kwargs: Any) -> Union[dict, list]:
    return to_serializable(await dispatch_to_response(*args, **kwargs))


async def dispatch_to_json(
    *args: Any, serializer: Callable = json.dumps, **kwargs: Any
) -> str:
    """
    This is the main public method, it goes through the entire JSON-RPC process
    - taking a JSON-RPC request string, dispatching it, converting the Response(s) into
    a serializable value and then serializing that to return a JSON-RPC response
    string.
    """
    return serializer(await dispatch_to_serializable(*args, **kwargs))


# "dispatch" is an alias of dispatch_to_json.
dispatch = dispatch_to_json
