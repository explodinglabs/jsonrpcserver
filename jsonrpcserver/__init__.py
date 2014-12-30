"""__init__.py"""

import logging

from flask import Blueprint

logger = logging.getLogger('jsonrpcserver')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)

bp = Blueprint('bp', __name__)

from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver import exceptions
