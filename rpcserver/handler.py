"""handler.py"""

import os
import json

import jsonschema
from . import exceptions
from . import rpc

def convert_params_to_args_and_kwargs(params):
    """Takes the 'params' from the rpc request and converts it into args and
    kwargs to be passed through to the handler method.

    There are four possibilities for params:
        - No params at all.
        - args, eg. "params": [1, 2]
        - kwargs, eg. "params: {"foo": "bar"}
        - Both args and kwargs: [1, 2, {"foo: "bar"}]
    """

    args = kwargs = None

    if isinstance(params, dict):
        kwargs = params

    elif isinstance(params, list):
        if isinstance(params[-1], dict):
            kwargs = params.pop()
        args = params

    return (args, kwargs)

#pylint:disable=star-args
def dispatch(handler, method_name, args, kwargs):
    """Call a handler method"""

    # Dont allow magic methods to be called
    if method_name.startswith('__') and method_name.endswith('__'):
        raise exceptions.MethodNotFound()

    # Get the method if available
    try:
        method = getattr(handler, method_name)

    # Catch method not found
    except AttributeError:
        raise exceptions.MethodNotFound()

    try:

        # Call the method
        if not args and not kwargs:
            return method()

        if args and not kwargs:
            return method(*args)

        if not args and kwargs:
            return method(**kwargs)

        if args and kwargs:
            return method(*args, **kwargs)

    # Catch argument mismatch errors
    except TypeError as e:
        raise exceptions.InvalidParams()

def handle(handler, request):

    try:
        # Validate
        try:
            jsonschema.validate(
                request,
                json.loads(open(os.path.dirname(__file__)+ \
                    '/request-schema.json').read()))

        except jsonschema.ValidationError:
            raise exceptions.InvalidRequest()

        # Get the args and kwargs from request['params']
        (args, kwargs) = convert_params_to_args_and_kwargs(
            request.get('params', None))

        result = dispatch(handler, request['method'], args, kwargs)

        # Call the handler method
        return rpc.result(request.get('id', None), result)

    # Catch any rpchandler error (invalid request etc), add the request id
    except exceptions.RPCHandlerException as e:
        e.request_id = request.get('id', None)
        raise
