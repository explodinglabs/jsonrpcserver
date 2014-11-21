jsonrpcserver
=============

`JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ client library for Python 3.

.. sourcecode:: python

    """views.py"""

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

.. sourcecode:: python

    app = flask.Flask(__name__)
    app.register_blueprint(jsonrpcserver.bp)

The blueprint's purpose is to handle errors. The app should respond with
JSON-RPC every time, for example if the requested method was invalid, it will
respond with the JSON-RPC error, *Method not found*.

Route
-----

Add a route to accept the RPC calls:

.. sourcecode:: python

    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

``dispatch`` is the key method in this library. It validates the RPC request,
and passes the data along to a function to handle. The argument passed to
``dispatch`` can be any collection of functions, such as a class or module. Here
we've passed this module, to handle the requests right here.

Handlers
--------

Write functions to handle each of the RPC requests:

.. sourcecode:: python

    def add(num1, num2):
        return num1 + num2

The RPC handling functions can receive any combination of positional or keyword
expansion arguments.

.. sourcecode:: python

    def find(name, *args, **kwargs):
        pass

Exceptions
----------

If the arguments received are invalid, raise the ``InvalidParams`` exception:

.. sourcecode:: python

    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except TypeError:
            raise jsonrpcserver.exceptions.InvalidParams()

Issue tracker is `here
<https://bitbucket.org/beau-barker/jsonrpcclient/issues>`_.

