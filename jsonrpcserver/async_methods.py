from .methods import Methods
from .async_dispatcher import dispatch

class AsyncMethods(Methods):

    async def dispatch(self, request):
        return await dispatch(self, request)

    def serve_forever(self):
        raise NotImplementedError()
