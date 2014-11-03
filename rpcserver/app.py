"""app.py"""

import os
import logging
import re
import json

import flask
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
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

def error(e, response_str):
    """Ensure we always respond with jsonrpc, such as on 400 or other bad
    request"""

    logging.info('<-- '+response_str)
    response = flask.Response(response_str, mimetype='application/json')
    response.status_code = (e.code if isinstance(e, HTTPException) else 500)
    return response

def invalid_request(e):
    return error(e, str(exceptions.InvalidRequest()))

def internal_error(e):
    return error(e, str(exceptions.InternalError()))

def handler_error(e):
    """RPCHandlerExceptions: responds with json"""

    return error(e, str(e))

class App(flask.Flask):
    """RPC App"""

    def __init__(self, import_name):
        super().__init__(import_name)

        # Override flask internal error handlers, to return as jsonrpc
        for code in default_exceptions.keys():

            # Client error
            if 400 <= code <= 499:
                self.error_handler_spec[None][code] = invalid_request

            # Server error
            else:
                self.error_handler_spec[None][code] = internal_error

        # Catch RPCHandler exceptions and return jsonrpc
        self.errorhandler(exceptions.RPCHandlerException)(handler_error)

        # Setup route
        self.route('/', methods=['POST'])(self.handle)

    def dispatch(self, method_name, args, kwargs):
        """Call a handler method"""

        # Dont allow magic methods to be called
        if method_name.startswith('__') and method_name.endswith('__'):
            raise exceptions.MethodNotFound()

        # Get the method if available
        try:
            method = getattr(self, method_name)

        # Catch method not found
        except AttributeError:
            raise exceptions.MethodNotFound()

        try:
            # Call the method
            if not args and not kwargs:
                return method()

            if args and not kwargs:
                return method(*args) #pylint:disable=star-args

            if not args and kwargs:
                return method(**kwargs) #pylint:disable=star-args

            if args and kwargs:
                return method(*args, **kwargs) #pylint:disable=star-args

        # Catch argument mismatch errors
        except TypeError as e:
            raise exceptions.InvalidParams(str(e))

    def handle(self):
        """Handle the request and output it"""

        # Get the request (this raises "400: Bad request" if fails)
        request = flask.request.get_json()
        logging.info('--> '+json.dumps(request))

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

            result = self.dispatch(request['method'], args, kwargs)

            if 'id' in request:
                response = rpc.result(request.get('id', None), result)
                logging.info('<-- '+json.dumps(response))
                return flask.jsonify(response)
            else:
                return ''

        # Catch any rpchandler error (invalid request etc), add the request id
        except exceptions.RPCHandlerException as e:
            if request:
                e.request_id = request.get('id', None)
            raise
