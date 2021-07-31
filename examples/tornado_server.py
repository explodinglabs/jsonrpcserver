from tornado import ioloop, web
from jsonrpcserver import Success, method, async_dispatch as dispatch


@method
async def ping() -> str:
    return Success("pong")


class MainHandler(web.RequestHandler):
    async def post(self) -> None:
        request = self.request.body.decode()
        if response := await dispatch(request):
            self.write(response)


app = web.Application([(r"/", MainHandler)])

if __name__ == "__main__":
    app.listen(5000)
    ioloop.IOLoop.current().start()
