"""__init__.py"""

from logging import getLogger, StreamHandler

from flask import Blueprint
from werkzeug.exceptions import default_exceptions

request_log = getLogger('jsonrpcserver.request')
response_log = getLogger('jsonrpcserver.response')
bp = Blueprint('bp', __name__)

from jsonrpcserver.blueprint import client_error, server_error
from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver import exceptions, status

# Override Flask's internal error handlers, to ensure we always return JSON-RPC
for code in default_exceptions.keys():

    # Client errors (4xx) should respond with "Invalid request"
    if status.is_http_client_error(code):
        bp.app_errorhandler(code)(client_error)

    # Everything else should respond with "Server error"
    else:
        bp.app_errorhandler(code)(server_error)
