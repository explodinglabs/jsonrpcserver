jsonrpcserver
=============

`JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ server library for Python 3.

Create a file named ``views.py``, and paste the following code:

.. sourcecode:: python

    import sys, flask, jsonrpcserver

    app = flask.Flask(__name__)

    # Blueprint
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

    # Blueprint
    app.register_blueprint(jsonrpcserver.bp)

The blueprint's purpose is to handle errors. The app should respond with
JSON-RPC every time; for example if the requested method was invalid, it will
respond with the JSON-RPC error, *Method not found*.

Note: When debugging your app, it can help to comment out the blueprint line,
so you get the tracebacks instead of just a jsonrpc error string.

Route
-----

Add a route to accept the RPC calls:

.. sourcecode:: python

    # Route
    @app.route('/', methods=['POST'])
    def index():
        return jsonrpcserver.dispatch(sys.modules[__name__])

``dispatch`` is the key method in this library. It validates the RPC request,
and passes the data along to a function to handle. The argument passed to
``dispatch`` can be any object that has functions, such as a class or module.
Here we've passed this module, to handle the requests right here.

Handlers
--------

Write functions to handle each of the RPC requests:

.. sourcecode:: python

    # Handlers
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
        except TypeError as e:
            raise jsonrpcserver.exceptions.InvalidParams(str(e))

Logging
-------

To see the underlying JSON messages, set the logging level to INFO:

.. sourcecode:: python

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

Issue tracker is `here
<https://bitbucket.org/beau-barker/jsonrpcserver/issues>`_.

If you need a client, try my `jsonrpcclient
<https://pypi.python.org/pypi/jsonrpcclient>`_ library.

Changelog
---------

1.0.5 - 2014-12-02
    * Messages are now output on the INFO log level.
    * Show the status code in response log entries

1.0.4 - 2014-11-22
    * Fixed readme

1.0.3 - 2014-11-21
    * The underlying JSON messages are now hidden by default. To see them you
      should increase the logging level (see above).
    * Tests moved into separate "tests" dir.
