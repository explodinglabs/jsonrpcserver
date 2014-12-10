"""blueprint.py"""

import flask
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import default_exceptions

from jsonrpcserver import exceptions, logger, bp, status


def flask_error_response(http_status_code, text):
    """This is a base function called by the others in this file. Takes an error
    message and status code, and returns a flask.Response object."""

    response = flask.Response(text, mimetype='application/json')
    response.status_code = http_status_code
    logger.info('<-- {} {}'.format(http_status_code, text))
    return response


@bp.app_errorhandler(exceptions.JsonRpcServerError)
def handler_error(jsonrpcerror):
    """Catch any exceptions raised by the library, and return as jsonrpc."""

    return flask_error_response(
        jsonrpcerror.http_status_code, str(jsonrpcerror))


def client_error(e):
    """Handle client errors caught by flask."""

    # For 404, raise MethodNotFound
    if e.code == status.HTTP_404_NOT_FOUND:
        return flask_error_response(
            e.code, str(exceptions.MethodNotFound(HTTP_STATUS_CODES[e.code])))

    else: # Anything else, raise InvalidRequest
        return flask_error_response(
            e.code, str(exceptions.InvalidRequest(HTTP_STATUS_CODES[e.code])))


def server_error(e):
    """Handle server errors caught by flask."""

    return flask_error_response(
        e.code, str(exceptions.ServerError(HTTP_STATUS_CODES[e.code])))


# Override flask internal error handlers, to always return as jsonrpc
for code in default_exceptions.keys():

    # Client errors should respond with jsonrpc "Invalid request" message
    if status.is_http_client_error(code):
        bp.app_errorhandler(code)(client_error)

    # Everything else should respond with jsonrpc "Server error" message
    else:
        bp.app_errorhandler(code)(server_error)
