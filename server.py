"""server.py"""

import logging
import re
import json

import flask
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
import jsonschema

from .handler import handle
from . import exceptions

class Server(flask.Flask):
    """RPC Server"""

    @staticmethod
    def make_json_error(e):
        """Ensure we always respond with jsonrpc, even on 404 or other bad
        request"""

        response_str = '{"jsonrpc": "2.0", "error": {"code": -1, "message": '+str(e)+'}, "id": null}'
        logging.info('<-- '+response_str)

        response = flask.Response(response_str, mimetype='application/json')
        response.status_code = (e.code if isinstance(e, HTTPException) else 500)
        return response

    def __init__(self, import_name, handler):
        super().__init__(import_name)
        self.handler = handler

        for code in default_exceptions.keys():
            self.error_handler_spec[None][code] = self.make_json_error

        self.route('/in', methods=['POST'])(self.rpc)
        self.errorhandler(exceptions.RPCHandlerException)(handle_rpc_error)

    def rpc(self):
        """Handle the request and output it"""

        # Get the request (raises "400: Bad request" if fails)
        request = flask.request.get_json()

        # Log the request
        logging.info('--> '+json.dumps(request))
        handle(self.handler, request)

        logging.info('<-- '+json.dumps(response))
        return flask.jsonify(response)

    def handle_rpc_error(e):
        logging.info('<-- '+str(e))
        return flask.jsonify(str(e))
