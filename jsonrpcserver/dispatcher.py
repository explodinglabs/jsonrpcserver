"""dispatcher.py"""

import json
import logging
import pkgutil
from funcsigs import signature
from six import string_types

import jsonschema

from .rpc import rpc_success_response, sort_response
from .exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest, MethodNotFound, InvalidParams, ServerError
from .status import HTTP_STATUS_CODES


logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')

json_validator = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode('utf-8')))


def _get_arguments_from_request(request):
    """Takes the 'params' part of a JSON-RPC request and converts it to either
    positional or keyword arguments.

    Important to remember - a JSON-RPC can have positional *or* keyword
    arguments, but not both!

    Positional arguments will be represented as a list. Keyword arguments will
    be represented as a dict. A third option is that 'params' was omitted.
    There are no other acceptable options.

    See http://www.jsonrpc.org/specification#parameter_structures

    .. versionchanged:: 1.0.12
        No longer allows both args and kwargs, as per spec.

    :param request: JSON-RPC request.
    :returns: A tuple containing the positionals (in a list, or None) and
        keywords (in a dict, or None) extracted from the 'params' part of the
        request.
    :raises InvalidParams: 'params' was present, but was not a list or dict.
    """
    positionals = keywords = None
    params = request.get('params')
    # Was 'params' omitted from the request? Consider this as "no arguments were
    # passed".
    if 'params' not in request:
        pass
    # Is params is a JSON array? (represented in Python as a list) eg. "params":
    # ["foo", "bar"]. Consider this positional arguments.
    elif isinstance(params, list):
        positionals = params
    # Is params a JSON object? (represented in Python as a dict) eg. "params":
    # {"foo": "bar"}. Consider this keyword arguments.
    elif isinstance(params, dict):
        keywords = params
    # Anything else is invalid. (This should never happen if the request has
    # passed the schema validation.)
    else:
        raise InvalidParams('Params of type %s is not allowed' % \
            type(params).__name__)
    return (positionals, keywords)


def _call(func, *positionals, **keywords):
    """Call the method, first ensuring the arguments match the function
    signature
    """
    try:
        params = signature(func).bind(*positionals, **keywords)
    except TypeError as e:
        raise InvalidParams(str(e))
    # Call the method and return the result
    return func(*params.args, **params.kwargs)


class Dispatcher(object):
    """Holds a list of the rpc methods, and dispatches to them."""

    def __init__(self, debug=False):
        """
        :param debug: Debug mode - includes the 'data' property in error
            responses which contain (potentially sensitive) debugging info.
            Default is False.
        """
        self._rpc_methods = {}
        self.validate_requests = True
        self.debug = debug

    def register_method(self, func, name=None):
        """Add an RPC method to the list."""
        if name is None:
            name = func.__name__
        self._rpc_methods[name] = func
        return func

    def method(self, name):
        """Add an RPC method to the list. Can be used as a decorator."""
        def decorator(f): #pylint:disable=missing-docstring
            return self.register_method(f, name)
        return decorator

    def dispatch(self, request):
        """Dispatch requests to the RPC methods.

        .. versionchanged:: 1.0.12
            Sending "'id': null" will be treated as if no response is required.

        .. versionchanged:: 2.0.0
            Removed all flask code.
            No longer accepts a "handler".

        :param request: JSON-RPC request in string or dict format.
        :return: Tuple containing the JSON-RPC response and an HTTP status code,
            which can be used to respond to a client.
        """
        # If the request is in string format, convert it to a dict before
        # continuing
        if isinstance(request, string_types):
            # Log the request before parsing
            request_log.info(request)
            try:
                request = json.loads(request)
            except ValueError:
                return (json.loads(str(ParseError())), 400)
        else:
            # Must already be a dict. Log before continuing.
            request_log.info(json.dumps(request))

        try:

            # Validate
            if self.validate_requests:
                try:
                    json_validator.validate(request)
                except jsonschema.ValidationError as e:
                    raise InvalidRequest(e.message)

            # Get the requested method, raise if unknown
            request_method = request['method']
            try:
                method = self._rpc_methods[request_method]
            except KeyError:
                raise MethodNotFound(request_method)

            # Get the positional and keyword arguments from the 'params' part
            (positionals, keywords) = _get_arguments_from_request(request)

            # Call the method, first ensuring the arguments match the function
            # signature
            if positionals:
                result = _call(method, *positionals)
            elif keywords:
                result = _call(method, **keywords)
            else:
                result = _call(method)

            # Build a response message
            request_id = request.get('id')
            if request_id is not None:
                # A response was requested
                response, status = (rpc_success_response(request_id, result), \
                    200)
            else:
                # Notification - return no content.
                response, status = (None, 204)

        # Catch JsonRpcServerErrors raised (invalid request etc)
        except JsonRpcServerError as e:
            e.request_id = request.get('id')
            response, status = (json.loads(str(e)), e.http_status_code)
            if not self.debug:
                response['error'].pop('data')

        # Catch all other exceptions, respond with ServerError message
        except Exception as e: #pylint:disable=broad-except
            logger.exception(e)
            response, status = (json.loads(str(ServerError(
                'See server logs'))), 500)
            if not self.debug:
                response['error'].pop('data')

        # Log the response
        response_log.info(str(sort_response(response)), extra={
            'http_code': status,
            'http_reason': HTTP_STATUS_CODES[status]
        })

        return (response, status)
