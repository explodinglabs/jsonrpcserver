.. rubric:: :doc:`index`

jsonrpcserver Examples
**********************

How to receive JSON-RPC requests in Python using various frameworks and
transport protocols.

.. contents::
    :local:

Plain jsonrpcserver
===================

Using jsonrpcserver's built-in `serve_forever` method.

::

    $ pip install jsonrpcserver

The quickest way to start the server::

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
        r = dispatch(methods, request.get_data().decode('utf-8'))
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
            request = self.rfile.read(int(self.headers['Content-Length'])).decode('utf-8')
            r = dispatch(methods, request)
            # Return response
            self.send_response(r.http_status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(str(r).encode('utf-8'))

    if __name__ == '__main__':
        HTTPServer(('localhost', 5000), TestHttpServer).serve_forever()

See `blog post <https://bcb.github.io/jsonrpc/httpserver>`__.

Socket.IO
=========

::

    $ pip install jsonrpcserver flask-socketio eventlet

::

    from flask import Flask
    from flask_socketio import SocketIO
    from jsonrpcserver import Methods, dispatch

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
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

    $ pip install tornado jsonrpcserver

::

    from tornado import ioloop, web
    from jsonrpcserver import Methods, dispatch

    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    class MainHandler(web.RequestHandler):
        def post(self):
            response = dispatch(methods, self.request.body.decode('utf-8'))
            self.write(response)

    if __name__ == "__main__":
        app = web.Application([(r"/", MainHandler)])
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
        r = dispatch(methods, request.data.decode('utf-8'))
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

    @methods.add
    def ping():
        return 'pong'

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind('tcp://*:5000')

    while True:
        request = socket.recv().decode('UTF-8')
        response = dispatch(methods, request)
        socket.send_string(str(response))

See `blog post <https://bcb.github.io/jsonrpc/pyzmq>`__.
