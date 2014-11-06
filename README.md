jsonrpcserver
=============

A [JSON-RPC 2.0](http://www.jsonrpc.org/) server library for Python 3.

Usage
-----

    # views.py

    import sys, flask, jsonrpcserver

    # Blueprint
    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

    # Route
    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

    # Handlers
    def add(num1, num2):
        return num1 + num2

    if __name__ == '__main__':
        app.run()

Test with:

    python -m views

What's going on here?

Blueprint
---------

Create a Flask app, and register the jsonrpcserver blueprint to it.

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

The blueprint's purpose is to handle errors. The app should respond with
JSON-RPC every time, for example if the requested method was invalid, it will
respond with the JSON-RPC error, *Method not found*.

Route
-----

Now create a route to accept the RPC calls:

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

``dispatch`` is the key method in this library. It validates the RPC request,
and passes the data along to a function to handle. The argument passed to
``dispatch`` can be any collection of functions, such as a class or module. We
passed this module to handle them right here.

Handlers
--------

Write functions to handle RPC requests, as you would any other Python function:

    def add(num1, num2):
        return num1 + num2

The RPC handling functions can receive any combination of positional, positional
expansion or keyword expansion arguments.

    def find(name, *args, **kwargs):
        pass

Exceptions
----------

If the arguments received are invalid, raise the ``InvalidParams`` exception:

    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except TypeError:
            raise jsonrpcserver.exceptions.InvalidParams()


If you need a client, try my
[jsonrpcclient](https://bitbucket.org/beau-barker/jsonrpcclient) library.
