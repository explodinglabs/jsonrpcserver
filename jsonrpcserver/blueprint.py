"""blueprint.py"""

import flask
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions

from jsonrpcserver import exceptions
from jsonrpcserver import logger
from jsonrpcserver import bp


def error(e, response_str):
    """Ensure we always respond with jsonrpc, such as on 400 or other bad
    request"""

    response = flask.Response(response_str, mimetype='application/json')
    response.status_code = (e.code if isinstance(e, HTTPException) else 400)
    logger.info('<-- {} {}'.format(response.status_code, response_str))
    return response


def invalid_request(e):
    """Status codes 400-499"""

    return error(e, str(exceptions.InvalidRequest()))


def internal_error(e):
    """Any error other than status codes 400-499"""

    return error(e, str(exceptions.InternalError()))


# Override flask internal error handlers, to return as jsonrpc
for code in default_exceptions.keys():
    if 400 <= code <= 499:
        bp.app_errorhandler(code)(invalid_request)
    else:
        bp.app_errorhandler(code)(internal_error)


# Catch RPCHandler exceptions and return jsonrpc
@bp.app_errorhandler(exceptions.RPCHandlerException)
def handler_error(e):
    """RPCHandlerExceptions: responds with json"""

    return error(e, str(e))
