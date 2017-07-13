"""Asynchronous methods"""
from .async_methods import AsyncMethods
from .async_dispatcher import dispatch # pylint:disable=unused-import

# A default AsyncMethods object which can be used, or user can create their own.
methods = AsyncMethods()
