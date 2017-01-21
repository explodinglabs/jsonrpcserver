"""jsonrpcserver.__init__"""
from .methods import Methods
from .dispatcher import dispatch

# A default Methods object which can be used, or user can create their own.
methods = Methods()
