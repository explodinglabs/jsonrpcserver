"""jsonrpcserver"""

import logging

from flask import Blueprint

logger = logging.getLogger('jsonrpcserver')
logger.addHandler(logging.StreamHandler())

bp = Blueprint('bp', __name__)

from . import exceptions
from .dispatch import dispatch
from . import blueprint
