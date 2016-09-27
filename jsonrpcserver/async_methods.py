"""Python 3.5+ users can dispatch requests asynchronously to coroutines.

Use methods the same way as before, but this time import from
``jsonrpcserver.aio``::

    from jsonrpcserver.aio import methods

    @methods.add
    async def ping():
        return await some_long_running_task()

You can then ``await`` the dispatch::

    await methods.dispatch(request)
"""
from .methods import Methods
from .async_dispatcher import dispatch

class AsyncMethods(Methods):

    async def dispatch(self, request):
        return await dispatch(self, request)

    def serve_forever(self):
        raise NotImplementedError()
