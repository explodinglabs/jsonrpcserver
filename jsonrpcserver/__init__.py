"""__init__.py"""

import logging

from flask import Blueprint

logger = logging.getLogger('jsonrpcserver')
logger.addHandler(logging.StreamHandler())

bp = Blueprint('bp', __name__)

import exceptions
import blueprint
from dispatch import dispatch
