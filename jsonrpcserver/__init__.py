"""
jsonrpcserver
*************
"""

import logging
logging.getLogger('jsonrpcserver').addHandler(logging.NullHandler())

from jsonrpcserver.methods import Methods
from jsonrpcserver.dispatcher import dispatch
