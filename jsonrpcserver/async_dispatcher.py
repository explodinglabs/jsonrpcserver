"""Asynchronous dispatch"""
import asyncio
import logging

from . import config
from .async_request import AsyncRequest
from .dispatcher import load_from_json, validate, request_logger, log_response
from .exceptions import JsonRpcServerError
from .log import log
from .response import BatchResponse, NotificationResponse, ExceptionResponse


async def dispatch(
    methods,
    requests,
    context=None,
    convert_camel_case=None,
    debug=None,
    notification_errors=None,
    schema_validation=None,
    trim_log_values=None,
):
    """
    Dispatch a request to a method.
    """
    # Some ugly code here to support the old config module which will be removed in 4.0,
    # and replaced with default arguments in the params of this function.
    convert_camel_case = (
        config.convert_camel_case if convert_camel_case is None else convert_camel_case
    )
    debug = config.debug if debug is None else debug
    notification_errors = (
        config.notification_errors
        if notification_errors is None
        else notification_errors
    )
    schema_validation = (
        config.schema_validation if schema_validation is None else schema_validation
    )
    trim_log_values = config.trim_log_values if trim_log_values is None else trim_log_values

    # TODO: Remove this predicate in version 4; configure logging Pythonically
    if config.log_requests:
        log(request_logger, logging.INFO, requests, fmt="--> %(message)s", trim=trim_log_values)

    try:
        requests = validate(load_from_json(requests))
    except JsonRpcServerError as exc:
        response = ExceptionResponse(exc, None, debug=debug)
    else:
        kwargs = dict(
            context=context,
            convert_camel_case=convert_camel_case,
            debug=debug,
            notification_errors=notification_errors,
            schema_validation=schema_validation,
        )
        if isinstance(requests, list):
            # Batch request
            responses = (AsyncRequest(r, **kwargs).call(methods) for r in requests)
            # Group async tasks
            responses = await asyncio.gather(*responses)
            # Remove notifications; batch request do not include them, as per spec
            responses = [r for r in responses if not r.is_notification]
            # If the response list is empty, return nothing
            response = BatchResponse(responses) if responses else NotificationResponse()
        # Single request
        else:
            response = await AsyncRequest(requests, **kwargs).call(methods)

    # TODO: Remove this predicate in version 4; configure logging Pythonically
    if config.log_responses:
        log_response(response, trim=trim_log_values)
    return response
