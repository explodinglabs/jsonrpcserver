"""dispatch.py"""

import json
import logging
import flask
from flask import g

from . import rpc
from . import exceptions

def convert_params_to_args_and_kwargs(params):
    """Takes the 'params' from the rpc request and converts it into args and
    kwargs to be passed through to the handler method.

    There are four possibilities for params:
        - No params at all.
        - args, eg. "params": [1, 2]
        - kwargs, eg. "params: {"foo": "bar"}
        - Both args and kwargs: [1, 2, {"foo": "bar"}]
    """

    args = kwargs = None

    if isinstance(params, dict):
        kwargs = params

    elif isinstance(params, list):
        if isinstance(params[-1], dict):
            kwargs = params.pop()
        args = params

    return (args, kwargs)

def dispatch(handler, method_name, params):
    """Call a handler method"""

    try:
        # Get the args and kwargs from request['params']
        (a, k) = convert_params_to_args_and_kwargs(params)

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
            if not a and not k:
                result = method()

            if a and not k:
                result = method(*a) #pylint:disable=star-args

            if not a and k:
                result = method(**k) #pylint:disable=star-args

            if a and k:
                result = method(*a, **k) #pylint:disable=star-args

            # Return, if a response was requested
            if 'id' in g.request:
                response = rpc.result(g.request.get('id', None), result)
                logging.info('<-- '+json.dumps(response))
                return flask.jsonify(response)
            else:
                return flask.Response('')

        # Catch argument mismatch errors
        except TypeError as e:
            raise exceptions.InvalidParams(str(e))

    # Catch any rpchandler error (invalid request etc), add the request id
    except exceptions.RPCHandlerException as e:
        if g.request:
            e.request_id = g.request.get('id', None)
        raise
