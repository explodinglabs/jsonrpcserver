.. rubric:: :doc:`index`

jsonrpcserver Examples
**********************

Showing how to take JSON-RPC requests in various frameworks and transport
protocols.

.. contents::
    :local:

aiohttp
=======

::

    $ pip install jsonrpcserver aiohttp

::

    from aiohttp import web
    from jsonrpcserver import Methods, dispatch

    app = web.Application()
    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    async def handle(request):
        request = await request.text()
        response = dispatch(methods, request)
        return web.json_response(response)

    app.router.add_post('/', handle)

    if __name__ == '__main__':
        web.run_app(app, port=5000)

Flask
=====

::

    $ pip install jsonrpcserver flask

::

    from flask import Flask, request, Response
    from jsonrpcserver import Methods, dispatch

    app = Flask(__name__)
    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    @app.route('/', methods=['POST'])
    def index():
        r = dispatch(methods, request.get_data().decode())
        return Response(str(r), r.http_status, mimetype='application/json')

    if __name__ == '__main__':
        app.run()

See `blog post <https://bcb.github.io/jsonrpc/flask>`__.

http.server
===========

Python's built-in `http.server
<https://docs.python.org/3/library/http.server.html>`__ module.

::

    $ pip install jsonrpcserver

::

    from http.server import BaseHTTPRequestHandler, HTTPServer
    from jsonrpcserver import Methods, dispatch

    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    class TestHttpServer(BaseHTTPRequestHandler):
        def do_POST(self):
            # Process request
            request = self.rfile.read(int(self.headers['Content-Length'])).decode()
            r = dispatch(methods, request)
            # Return response
            self.send_response(r.http_status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str(r).encode())

    if __name__ == '__main__':
        HTTPServer(('localhost', 5000), TestHttpServer).serve_forever()

See `blog post <https://bcb.github.io/jsonrpc/httpserver>`__.

Plain jsonrpcserver
===================

Using jsonrpcserver's built-in `serve_forever` method.

::

    $ pip install jsonrpcserver

The quickest way to serve a method::

    from jsonrpcserver import Methods
    Methods(ping=lambda:'pong').serve_forever()

Using the `@methods` decorator::

    from jsonrpcserver import Methods

    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    if __name__ == '__main__':
        methods.serve_forever()

Socket.IO
=========

::

    $ pip install jsonrpcserver flask flask-socketio eventlet

::

    from flask import Flask
    from flask_socketio import SocketIO
    from jsonrpcserver import Methods, dispatch

    app = Flask(__name__)
    socketio = SocketIO(app)
    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    @socketio.on('message')
    def handle_message(request):
        return dispatch(methods, request)

    if __name__ == '__main__':
        socketio.run(app, port=5000)

See `blog post <https://bcb.github.io/jsonrpc/flask-socketio>`__.

Tornado
=======

::

    $ pip install jsonrpcserver tornado

::

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

See `blog post <https://bcb.github.io/jsonrpc/tornado>`__.

Werkzeug
========

::

    $ pip install jsonrpcserver werkzeug

::

    from werkzeug.wrappers import Request, Response
    from werkzeug.serving import run_simple
    from jsonrpcserver import Methods, dispatch

    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    @Request.application
    def application(request):
        r = dispatch(methods, request.data.decode())
        return Response(str(r), r.http_status, mimetype='application/json')

    if __name__ == '__main__':
        run_simple('localhost', 5000, application)

See `blog post <https://bcb.github.io/jsonrpc/werkzeug>`__.

ZeroMQ
======

::

    $ pip install jsonrpcserver pyzmq

::

    import zmq
    from jsonrpcserver import Methods, dispatch

    methods = Methods()
    socket = zmq.Context().socket(zmq.REP)

    @methods.add
    def ping():
        return 'pong'

    if __name__ == '__main__':
        socket.bind('tcp://*:5000')
        while True:
            request = socket.recv().decode()
            response = dispatch(methods, request)
            socket.send_string(str(response))

See `blog post <https://bcb.github.io/jsonrpc/zeromq>`__.
