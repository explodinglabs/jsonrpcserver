"""Asynchronous dispatch"""
import asyncio

from . import config
from .async_request import AsyncRequest
from .dispatcher import (
    load_from_json,
    validate,
    request_logger,
    log_response,
)
from .log import log
from .response import BatchResponse, NotificationResponse, ExceptionResponse
from .exceptions import JsonRpcServerError


async def dispatch(methods, requests, context=None):
    """Main public dispatch method."""
    if config.log_requests:
        log(request_logger, "info", requests, fmt="--> %(message)s")
    try:
        requests = validate(load_from_json(requests))
    except JsonRpcServerError as exc:
        response = ExceptionResponse(exc, None)
    else:
        # Batch requests
        if isinstance(requests, list):
            response = await asyncio.gather(
                *[AsyncRequest(r, context=context).call(methods) for r in requests]
            )
            # Responses to batch requests should not contain notifications, as per spec
            response = [r for r in response if not r.is_notification]
            # If the response list is empty, return nothing
            response = BatchResponse(response) if response else NotificationResponse()
        # Single request
        else:
            response = await AsyncRequest(requests, context=context).call(methods)
    if config.log_responses:
        log_response(response)
    return response
