"""Asynchronous methods"""
from .async_dispatcher import dispatch # pylint:disable=unused-import
from .async_methods import AsyncMethods

# A default AsyncMethods object which can be used, or user can create their own.
methods = AsyncMethods()
