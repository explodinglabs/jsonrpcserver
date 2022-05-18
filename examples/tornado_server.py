from jsonrpcserver import async_dispatch, async_method, Ok, Result
from tornado import ioloop, web


@async_method
async def ping() -> Result:
    return Ok("pong")


class MainHandler(web.RequestHandler):
    async def post(self) -> None:
        request = self.request.body.decode()
        if response := await async_dispatch(request):
            self.write(response)


app = web.Application([(r"/", MainHandler)])

if __name__ == "__main__":
    app.listen(5000)
    ioloop.IOLoop.current().start()
