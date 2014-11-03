"""server.py"""

import os
import logging
import re
import json

import flask
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
import jsonschema

from . import exceptions

class Server(flask.Flask):
    """RPC Server"""

    @staticmethod
    def flask_error(e):
        """Ensure we always respond with jsonrpc, even on 404 or other bad
        request"""

        response_str = '{"jsonrpc": "2.0", "error": {"code": -1, "message": "'+str(e)+'"}, "id": null}'
        logging.info('<-- '+response_str)

        response = flask.Response(response_str, mimetype='application/json')
        response.status_code = (e.code if isinstance(e, HTTPException) else 500)
        return response

    def __init__(self, import_name):
        super().__init__(import_name)

        # Catch flask errors such as 400 Bad Request and return as jsonrpc
        for code in default_exceptions.keys():
            self.error_handler_spec[None][code] = self.flask_error

        self.route('/', methods=['POST'])(self.handle)

    def dispatch(method_name, args, kwargs):
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

        # Get the request (raises "400: Bad request" if fails)
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

            result = dispatch(request['method'], args, kwargs)

            # Call the handler method
            response = rpc.result(request.get('id', None), result)

        # Catch any rpchandler error (invalid request etc), add the request id
        except exceptions.RPCHandlerException as e:
            e.request_id = request.get('id', None)
            raise

        logging.info('<-- '+json.dumps(response))
        return flask.jsonify(response)
