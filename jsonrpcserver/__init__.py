"""__init__.py"""

from logging import getLogger, StreamHandler

from flask import Blueprint

request_log = getLogger('jsonrpcserver.request')
response_log = getLogger('jsonrpcserver.response')

bp = Blueprint('bp', __name__)

from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver import exceptions
