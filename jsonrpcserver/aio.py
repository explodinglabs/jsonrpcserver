"""Asynchronous methods"""
from .async_methods import AsyncMethods
from .async_dispatcher import dispatch

# A default AsyncMethods object which can be used, or user can create their own.
methods = AsyncMethods()
