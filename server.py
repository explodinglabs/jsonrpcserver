"""server.py"""

import logging
import re
import json

import flask
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
import rpchandler

def make_json_error(e):
    """Ensure we respond with json every time. All error responses that you
    don't specifically manage yourself will have application/json content type.
    See http://flask.pocoo.org/snippets/83/"""

    response_str = '{"jsonrpc": "2.0", "error": {"code": -1, "message": "Internal Error"}, "id": null}'
    logging.info('<-- '+response_str)

    response = flask.Response(response_str, mimetype='application/json')
    response.status_code = (e.code if isinstance(e, HTTPException) else 500)
    return response

class Server(flask.Flask):
    """RPC Server"""

    def __init__(self, import_name, handler):
        super().__init__(import_name)
        self.config['JSON_SORT_KEYS'] = False
        self.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
        self.handler = handler

        for code in default_exceptions.keys():
            self.error_handler_spec[None][code] = make_json_error

        self.route('/in', methods=['POST'])(self.handle_rpc_request)

    def handle_rpc_request(self):
        """Handle the request and output it"""

        request = flask.request.get_json()

        # Log the request
        logging.info('--> '+json.dumps(request))

        try:
            response = rpchandler.handle(self.handler, request, True)
            logging.info('<-- '+json.dumps(response))
            return flask.jsonify(response)

        # Catch rpchandler error (invalid request etc)
        except rpchandler.exceptions.RPCHandlerException as e:
            logging.info('<-- '+str(e))
            return flask.Response(str(e), mimetype='application/json')
