from tornado import ioloop, web
from jsonrpcserver import Methods, dispatch

methods = Methods()

@methods.add
def ping():
    return 'pong'

class MainHandler(web.RequestHandler):
    def post(self):
        response = dispatch(methods, self.request.body.decode())
        self.write(response)

app = web.Application([(r"/", MainHandler)])

if __name__ == '__main__':
    app.listen(5000)
    ioloop.IOLoop.current().start()
