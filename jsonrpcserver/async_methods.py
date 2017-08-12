"""
Asynchronous methods.

Python 3.5+ users can dispatch requests to coroutines. Usage is the same as
synchronous methods, but this time import from ``jsonrpcserver.aio``::

    from jsonrpcserver.aio import methods

    @methods.add
    async def ping():
        return await some_long_running_task()

Then ``await`` the dispatch::

    response = await methods.dispatch(request)
"""
from .async_dispatcher import dispatch
from .methods import Methods


class AsyncMethods(Methods):

    async def dispatch(self, request, context=None):
        return await dispatch(self, request, context=context)

    def serve_forever(self):
        raise NotImplementedError()
