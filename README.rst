jsonrpcserver
=============

Take `JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

This package has two features:

#. A `blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ to handle
   errors, ensuring we always respond with json.

#. A ``dispatch`` method, which passes requests on to your own code in order to
   carry out the request.


Installation
------------

    pip install jsonrpcserver


Usage
-----

Create a Flask app and register the blueprint.

.. sourcecode:: python

    from flask import Flask
    from jsonrpcserver import bp, dispatch, exceptions

    app = Flask(__name__)
    app.register_blueprint(bp)

Add a route to dispatch requests to the handling methods.

.. sourcecode:: python

    @app.route('/', methods=['POST'])
    def index():
        return dispatch(HandleRequests)

Lastly, write the methods that will carry out the requests.

.. sourcecode:: python

    class HandleRequests:

        def add(num1, num2):
            return num1 + num2

These methods can take any number of positional or keyword arguments.

.. sourcecode:: python

    def find(name, age=42, *args, **kwargs):
        ...

When arguments are invalid, raise ``InvalidParams``.

.. sourcecode:: python

    def add(num1, num2):
        try:
            return num1 + num2
        except TypeError:
            raise exceptions.InvalidParams(str(e))

See it all put together `here
<https://bitbucket.org/beau-barker/jsonrpcserver/src/tip/run.py>`_.

.. note::

    To see the underlying messages going back and forth, set the logging level
    to INFO:

    ``logging.getLogger('jsonrpcserver').setLevel(logging.INFO)``

Issue tracker is `here
<https://bitbucket.org/beau-barker/jsonrpcserver/issues>`_.

If you need a client, try my `jsonrpcclient
<https://pypi.python.org/pypi/jsonrpcclient>`_ library.

Changelog
---------

1.0.6 - 2014-12-11
    * Improved blueprint, with correct http status code responses.
    * Gives more information when rejecting a request.
    * Major rebuild of the exceptions.
    * More stability with 100% code coverage in tests.

1.0.5 - 2014-12-02
    * Messages are now output on the INFO log level.
    * Show the status code in response log entries.

1.0.4 - 2014-11-22
    * Fixed readme.

1.0.3 - 2014-11-21
    * The underlying JSON messages are now hidden by default. To see them you
      should increase the logging level (see above).
    * Tests moved into separate "tests" dir.
