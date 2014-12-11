jsonrpcserver
=============

`JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ server library for Python 3.

Installation
------------

    pip install jsonrpcserver

Usage
-----

This library allows you to recieve `JSON-RPC 2.0 <http://www.jsonrpc.org/>`_
requests in a `Flask <http://flask.pocoo.org/>`_ app.

The library provides two features:

A blueprint for handling errors, ensuring we *always* respond with json.

.. sourcecode:: python

    # Create a flask app and register the blueprint
    app = Flask(__name__)
    app.register_blueprint(bp)

A ``dispatch()`` method for handling and dispatching requests.

.. sourcecode:: python

    # Create a route for access, and dispatch
    @app.route('/', methods=['POST'])
    def index():
        return dispatch(sys.modules[__name__])

Now you can write the RPC procedures, as you would any other python function:

.. sourcecode:: python

    def add(num1, num2='Not a number'):
        return num1 + num2


Validating arguments
--------------------

If the arguments received are invalid, raise the ``InvalidParams`` exception:

.. sourcecode:: python

    from jsonrpcserver.exceptions import InvalidParams
    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except TypeError as e:
            raise InvalidParams(str(e))

.. note::
    To see the underlying messages going back and forth, set the logging level
    to INFO:

    ``import logging; logging.getLogger('jsonrpcclient').setLevel(logging.INFO)``


Issue tracker is `here
<https://bitbucket.org/beau-barker/jsonrpcserver/issues>`_.

If you need a client, try my `jsonrpcclient
<https://pypi.python.org/pypi/jsonrpcclient>`_ library.

Todo
----

More dispatch tests.

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
