from tornado import ioloop, web
from jsonrpcserver import methods
from jsonrpcserver.async_dispatcher import dispatch

@methods.add
async def ping():
    return 'pong'

class MainHandler(web.RequestHandler):
    async def post(self):
        response = await dispatch(methods, self.request.body.decode())
        self.write(response)

app = web.Application([(r"/", MainHandler)])

if __name__ == '__main__':
    app.listen(5000)
    ioloop.IOLoop.current().start()
