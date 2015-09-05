"""dispatcher.py"""

import json
import logging
import pkgutil
from inspect import getcallargs

import jsonschema

from jsonrpcserver import rpc
from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest, MethodNotFound, InvalidParams, ServerError
from jsonrpcserver.status import HTTP_STATUS_CODES


logger = logging.getLogger(__name__)
request_log = logging.getLogger(__name__+'.request')
response_log = logging.getLogger(__name__+'.response')

json_validator = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode('utf-8')))


def _convert_params_to_args_and_kwargs(params):
    """Takes the 'params' from the rpc request and converts it into args and
    kwargs to be passed through to the handling method.

    There are four possibilities for params:
        - No params at all.
        - args, eg. "params": [1, 2]
        - kwargs, eg. "params: {"foo": "bar"}
        - Both args and kwargs: [1, 2, {"foo": "bar"}]

    .. versionchanged:: 1.0.12
        No longer allows both args and kwargs, as per spec.

    :param params: The arguments for the JSON-RPC method.
    """
    args = kwargs = None
    # Params is a dict, ie. "params": {"foo": "bar"}
    if isinstance(params, dict):
        kwargs = params
    # Params is a list, ie. "params": ["foo", "bar"]
    elif isinstance(params, list):
        args = params
    return (args, kwargs)


class Dispatcher(object):
    """Holds a list of the rpc methods, and dispatches to them."""

    def __init__(self, debug=False):
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

        :param request: A JSON-RPC request in dict format.
        :return: A tuple containing the JSON-RPC response and an HTTP status
            code, which can be used to respond to a client.
        """
        #pylint:disable=too-many-branches,too-many-statements

        request_log.info(json.dumps(request))

        try:

            # Validate
            if self.validate_requests:
                try:
                    json_validator.validate(request)
                except jsonschema.ValidationError as e:
                    raise InvalidRequest(e.message)

            # Get the args and kwargs from request['params']
            (a, k) = _convert_params_to_args_and_kwargs(request.get('params', \
                None))

            request_method = request['method']

            # Dont allow magic methods to be called
            if request_method.startswith('__') and \
                    request_method.endswith('__'):
                raise MethodNotFound(request_method)

            # Get the method if available
            try:
                method = self._rpc_methods[request_method]
            except KeyError:
                raise MethodNotFound(request_method)

            # Call the method, first checking if the arguments match the
            # method's parameters. It's no good checking for invalid params by
            # simply calling the method, because the caught exception may have
            # been raised from inside the method. This section is ugly but I'm
            # yet to find a better option.
            if not a and not k:
                try:
                    getcallargs(method)
                except TypeError as e:
                    raise InvalidParams(str(e))
                method_result = method()

            if a and not k:
                try:
                    getcallargs(method, *a)
                except TypeError as e:
                    raise InvalidParams(str(e))
                method_result = method(*a)

            if not a and k:
                try:
                    getcallargs(method, **k)
                except TypeError as e:
                    raise InvalidParams(str(e))
                method_result = method(**k)

            # if a and k: # This should never happen.

            # Return a response
            request_id = request.get('id')
            if request_id is not None:
                # A response was requested
                result, status = (rpc.result(request_id, method_result), 200)
            else:
                # Notification - return nothing.
                result, status = (None, 204)

        # Catch JsonRpcServerErrors raised (invalid request etc)
        except JsonRpcServerError as e:
            e.request_id = request.get('id')
            result, status = (json.loads(str(e)), e.http_status_code)
            if not self.debug:
                result['error'].pop('data')

        # Catch all other exceptions
        except Exception as e: #pylint:disable=broad-except
            # Log the exception
            logging.exception(e)
            result, status = (json.loads(str(ServerError('See server logs'))), \
                500)
            if not self.debug:
                result['error'].pop('data')

        response_log.info(str(result), extra={
            'http_code': status,
            'http_reason': HTTP_STATUS_CODES[status]
        })

        return (result, status)

    def dispatch_str(self, request):
        """Wrapper for dispatch, which takes a string instead of a dict."""
        try:
            request = json.loads(request)
        except ValueError:
            raise ParseError()
        return self.dispatch(request)
