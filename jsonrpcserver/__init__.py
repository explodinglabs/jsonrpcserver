"""__init__.py"""

import logging

from flask import Blueprint

logger = logging.getLogger('jsonrpcserver')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)

bp = Blueprint('bp', __name__)

from jsonrpcserver import exceptions
from jsonrpcserver import blueprint
from jsonrpcserver.dispatch import dispatch
