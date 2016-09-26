"""jsonrpcserver.__init__"""
from .methods import Methods
from .dispatcher import dispatch

methods = Methods()
