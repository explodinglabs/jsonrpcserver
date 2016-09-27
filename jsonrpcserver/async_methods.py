"""
Added in version 3.4 is the ability for Python 3.5+ users to dispatch requests
asynchronously to coroutines.

Use the methods and dispatcher in the same way as before, but this time import
from ``jsonrpcserver.aio``::

    from jsonrpcserver.aio import methods

    @methods.add
    async def ping():
        return await some_long_running_task()

You can then ``await methods.dispatch(request)`` in your event loop.
"""

from .methods import Methods
from .async_dispatcher import dispatch

class AsyncMethods(Methods):

    async def dispatch(self, request):
        return await dispatch(self, request)

    def serve_forever(self):
        raise NotImplementedError()