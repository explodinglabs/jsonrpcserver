"""dispatcher.py"""
#pylint:disable=star-args

import json
import inspect

import jsonschema
import pkgutil
from inspect import getcallargs
from jsonrpcserver import rpc, exceptions, request_log, response_log
from jsonrpcserver.status import HTTP_STATUS_CODES


def convert_params_to_args_and_kwargs(params):
    """Takes the 'params' from the rpc request and converts it into args and
    kwargs to be passed through to the handler method.

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


def dispatch(request, handler=None):
    """Call a method, based on the request.

    request: A dict containing the JSON request.

    handler: An object containing the methods that carry out the requests. Can
    be any object that containing methods, such as a class with static methods,
    or a module. If no handler is passed, the calling module is used as the
    handler.

    ..versionchanged:: 1.0.12
        Sending "'id': null" will be treated as if no response is required.
    ..versionchanged:: 1.1.1
        Removed all flask code.
    """
    #pylint:disable=too-many-branches

    if not handler:
        handler = inspect.getmodule(inspect.stack()[1][0])

    request_log.info(json.dumps(request))

    try:

        # Validate
        try:
            jsonschema.validate(
                request, json.loads(pkgutil.get_data(__name__, \
                'request-schema.json').decode('utf-8')))
        except jsonschema.ValidationError as e:
            raise exceptions.InvalidRequest(e.message)


        # Get the args and kwargs from request['params']
        (a, k) = convert_params_to_args_and_kwargs(request.get('params', None))


        # Dont allow magic methods to be called
        if request['method'].startswith('__') \
                and request['method'].endswith('__'):
            raise exceptions.MethodNotFound(request['method'])


        # Get the method if available
        try:
            method = getattr(handler, request['method'])

        # Catch method not found
        except AttributeError:
            raise exceptions.MethodNotFound(request['method'])


        # Call the method
        if not a and not k:
            try:
                getcallargs(method)
            except TypeError as e:
                raise exceptions.InvalidParams(str(e))
            result = method()

        if a and not k:
            try:
                getcallargs(method, *a)
            except TypeError as e:
                raise exceptions.InvalidParams(str(e))
            result = method(*a)

        if not a and k:
            try:
                getcallargs(method, **k)
            except TypeError as e:
                raise exceptions.InvalidParams(str(e))
            result = method(**k)

#        if a and k: # should never happen
#            raise exceptions.InvalidParams('Using both positional and keyword \
#            arguments is not supported by the JSON-RPC protocol')

        # Return a response
        request_id = request.get('id', None)
        if request_id is not None:
            result, status = rpc.result(request_id, result), 200
            response_log.info(result, extra={
                'http_code': status,
                'http_reason': HTTP_STATUS_CODES[status]
            })
        else:
            result, status = None, 204
            response_log.info(result, extra={
                'http_code': status,
                'http_reason': HTTP_STATUS_CODES[status]
            })
        return result, status

    # Catch any raised exception (invalid request etc), add the request id
    except exceptions.JsonRpcServerError as e:
        if request:
            e.request_id = request.get('id', None)
        response = json.loads(str(e))
        response_log.info(str(e), extra={
            'http_code': e.http_status_code,
            'http_reason': HTTP_STATUS_CODES[e.http_status_code]
        })
        return response, e.http_status_code
