"""dispatcher.py"""

import json
import flask
import jsonschema
import pkgutil
from inspect import getcallargs

from jsonrpcserver import rpc, exceptions, request_log, response_log

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

def dispatch(handler):
    """Call a handler method"""
    #pylint:disable=star-args

    # Get the request (this raises "400: Bad request" if fails)
    request = flask.request.get_json()
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

        if a and k:
            try:
                getcallargs(method, *a, **k)
            except TypeError as e:
                raise exceptions.InvalidParams(str(e))
            result = method(*a, **k)

        # Return, if a response was requested
        if 'id' in request:
            response = rpc.result(request.get('id', None), result)
            response_log.info(json.dumps(response), extra={
                'http_code': 200,
                'http_reason': 'OK',
            })
            return flask.jsonify(response)
        else:
            return flask.Response('')

    # Catch any raised exception (invalid request etc), add the request id
    except exceptions.JsonRpcServerError as e:
        if request:
            e.request_id = request.get('id', None)
        raise
