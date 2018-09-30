from tornado import ioloop, web
from jsonrpcserver.aio import method, dispatch

@method
async def ping():
    return 'pong'

class MainHandler(web.RequestHandler):
    async def post(self):
        request = self.request.body.decode()
        response = await dispatch(request)
        if response.wanted:
            self.write(str(response))

app = web.Application([(r"/", MainHandler)])

if __name__ == '__main__':
    app.listen(5000)
    ioloop.IOLoop.current().start()
