"""Tornado server"""
from typing import Awaitable, Optional

from tornado import ioloop, web

from jsonrpcserver import Result, Success, async_dispatch, method


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


class MainHandler(web.RequestHandler):
    """Handle Tornado request"""

    async def post(self) -> None:
        """Post"""
        request = self.request.body.decode()
        response = await async_dispatch(request)
        if response:
            self.write(response)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


app = web.Application([(r"/", MainHandler)])

if __name__ == "__main__":
    app.listen(5000)
    ioloop.IOLoop.current().start()
