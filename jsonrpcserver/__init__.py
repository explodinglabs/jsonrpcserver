"""jsonrpcserver"""

from flask import Blueprint

from . import exceptions
from .dispatch import dispatch

bp = Blueprint('bp', __name__)

from . import blueprint
