"""dispatcher.py"""

import logging
import json

from funcsigs import signature

from .rpc import rpc_success_response, sort_response
from .request import Request
from .exceptions import JsonRpcServerError, InvalidParams, ServerError
from .status import HTTP_STATUS_CODES
from .methods import _get_method


logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')


def _validate_arguments_against_signature(func, args, kwargs):
    """
    Checks if arguments match a function signature and can therefore be passed
    to it.
    :param func: The function object.
    :param args: List of positional arguments (or None).
    :param kwargs: Dict of keyword arguments (or None).
    :raises InvalidParams: If the arguments cannot be passed to the function.
    :returns: None.
    """
    try:
        if not args and not kwargs:
            signature(func).bind()
        elif args:
            signature(func).bind(*args)
        elif kwargs:
            signature(func).bind(**kwargs)
    except TypeError as e:
        raise InvalidParams(str(e))


def _call(methods, method_name, args=None, kwargs=None):
    """
    Finds a method from a list, then validates the arguments before calling it.
    :param methods: The list of methods - either a python list, or Methods obj.
    :param args: Positional arguments (list)
    :param kwargs: Keyword arguments (dict)
    :raises MethodNotFound: If the method is not in the list.
    :raises InvalidParams: If the arguments don't match the method signature.
    :returns: The return value from the method called.
    """
    # Get the method object from a list of rpc methods
    method = _get_method(methods, method_name)
    # Ensure the arguments match the method's signature
    _validate_arguments_against_signature(method, args, kwargs)
    # Call the method
    if not args and not kwargs:
        return method()
    elif args:
        return method(*args)
    elif kwargs:
        return method(**kwargs)
    else:
        raise InvalidParams()


def dispatch(methods, request, debug=False):
    """
    Dispatch requests to the RPC methods.
    :param request: JSON-RPC request in dict or string format.
    :returns: Tuple containing information which can be used to respond to a
        client, such as the JSON-RPC response and an HTTP status code.
    """
    r = None
    try:
        # Log the request
        request_log.info(str(request))
        # Create request object (also validates the request)
        r = Request(request)
        result = _call(methods, r.method_name, r.args, r.kwargs)
    # Catch JsonRpcServerError raised (Invalid Request, etc)
    except JsonRpcServerError as e:
        if hasattr(r, 'request_id'):
            e.request_id = r.request_id
        response, status = (json.loads(str(e)), e.http_status_code)
        if not debug:
            response['error'].pop('data')
    # Catch all other exceptions, respond with ServerError message
    except Exception as e: #pylint:disable=broad-except
        logger.exception(e)
        response, status = (json.loads(str(ServerError(
            'See server logs'))), 500)
        if not debug:
            response['error'].pop('data')
    else:
        # Build a success response message
        if r.is_notification:
            # Notification - return no content.
            response, status = (None, 204)
        else:
            # A response was requested
            response, status = (rpc_success_response(r.request_id, result), 200)
    # Log the response
    response_log.info(json.dumps(sort_response(response)), extra={'http_code': \
        status, 'http_reason': HTTP_STATUS_CODES[status]})
    return (response, status)
