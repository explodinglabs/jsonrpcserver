from tornado import ioloop, web
from jsonrpcserver.aio import methods
from jsonrpcserver.response import NotificationResponse

@methods.add
async def ping():
    return 'pong'

class MainHandler(web.RequestHandler):
    async def post(self):
        request = self.request.body.decode()
        response = await methods.dispatch(request)
        if not isinstance(response, NotificationResponse):
            self.write(response)

app = web.Application([(r"/", MainHandler)])

if __name__ == '__main__':
    app.listen(5000)
    ioloop.IOLoop.current().start()
