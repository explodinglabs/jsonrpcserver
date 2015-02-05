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
