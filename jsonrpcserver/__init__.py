"""__init__.py"""
from .dispatcher import dispatch
from .methods import Methods

# A default Methods object which can be used, or user can create their own.
methods = Methods()
