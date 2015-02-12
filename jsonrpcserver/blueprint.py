"""blueprint.py"""

import json

from flask import Response, request
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import default_exceptions

from jsonrpcserver import exceptions, response_log, bp, status


def request_wants_json(accept_mimetypes):
    """Returns true if the Accept header is one of the acceptable options for
    JSON-RPC. (either application/json-rpc, application/json or
    application/jsonrpcrequest). Adapted from
    http://flask.pocoo.org/snippets/45/"""

    # Acceptable JSON-RPC mimetypes
    # from http://jsonrpc.org/historical/json-rpc-over-http.html#http-header
    jsonrpc_mimetypes = ['application/json-rpc', 'application/json', \
        'application/jsonrequest']

    jsonrpc_and_html_mimetypes = list(jsonrpc_mimetypes)
    jsonrpc_and_html_mimetypes.extend(['text/html'])

    best = accept_mimetypes.best_match(jsonrpc_and_html_mimetypes)
    return best in jsonrpc_mimetypes \
        and accept_mimetypes[best] > accept_mimetypes['text/html']


def flask_error_response(http_status_code, text):
    """This is a base function called by the others in this file. Takes an error
    message and status code, and returns a flask.Response object."""

    response = Response(text, mimetype='application/json')
    response.status_code = http_status_code
    response_log.info(text, extra={
        'http_code': response.status_code,
        'http_reason': HTTP_STATUS_CODES[response.status_code].upper(),
        'http_headers': json.dumps(dict(response.headers))
    })
    return response


def client_error(error):
    """Handle client errors caught by flask."""

    code = error.code

    # Do they want a JSON response? (Check the accept header.) If so, handle it
    # by returning JSON-RPC. Otherwise, return the default werkzeug response.
    if request.accept_mimetypes and \
            request_wants_json(request.accept_mimetypes):
        return flask_error_response(code, \
            str(exceptions.InvalidRequest(HTTP_STATUS_CODES[code])))
    else:
        return default_exceptions[code]().get_response()


def server_error(error):
    """Handle server errors caught by flask."""

    # Note, in the case of a syntax error, we get a TypeError, in which case we
    # should just use 500 Internal Server Error
    code = 500
    if hasattr(error, 'code'):
        code = error.code

    # Do they want a JSON response? (Check the accept header.) If so, handle it
    # by returning JSON-RPC. Otherwise, return the default werkzeug response.
    if request.accept_mimetypes and \
            request_wants_json(request.accept_mimetypes):
        return flask_error_response(code, \
            str(exceptions.ServerError(HTTP_STATUS_CODES[code])))
    else:
        return default_exceptions[code]().get_response()


@bp.app_errorhandler(exceptions.JsonRpcServerError)
def custom_exception_error_handler(exc):
    """Catch any JsonRpcServerError exception, and convert it to
    jsonrpc format."""

    return flask_error_response(exc.http_status_code, str(exc))


@bp.record_once
def set_errorhandlers(setup_state):
    """Set the errorhandlers for standard HTTP errors like 404. This is so we
    can return the error in JSON-RPC format (if they've asked for json in the
    Accept header)"""
    #pylint:disable=unused-argument

    # Override Flask's internal error handlers, to ensure we always return
    # JSON-RPC
    for code in default_exceptions.keys():

        # Client errors (4xx) should respond with "Invalid request"
        if status.is_http_client_error(code):
            bp.app_errorhandler(code)(client_error)

        # Everything else, respond with "Server error"
        else:
            bp.app_errorhandler(code)(server_error)


@bp.record_once
def store_options(setup_state):
    """Keeps a record of the kwargs passed to register_blueprint, for later
    access"""
    bp.options = setup_state.options


@bp.before_app_request
def check_request():
    """Can check bp.options here."""
    pass
