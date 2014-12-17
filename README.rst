jsonrpcserver
=============

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library has two features:

#. A dispatcher, which validates incoming requests and then passes them on to
   your own code to carry out the request.

#. A `Flask blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ to catch
   errors, ensuring we always respond with JSON-RPC.

Installation
------------

::

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

Now go ahead and write the methods that will carry out the requests.

.. sourcecode:: python

    class HandleRequests:
        def add(x, y):
            return x + y

Keyword arguments are also allowed.

.. sourcecode:: python

    def find(name='Foo', age=42, **kwargs):

.. important::

    Use either positional or keyword arguments, but not both in the same
    method. See `Parameter Structures
    <http://www.jsonrpc.org/specification#parameter_structures>`_ in the
    specs.

When arguments are invalid, raise ``InvalidParams``.

.. sourcecode:: python

    def add(x, y):
        try:
            return x + y
        except TypeError as e:
            raise exceptions.InvalidParams('Type error')

The blueprint will catch the exception and ensure this is returned::

    {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": "Type error"}, "id": 1}

See it all put together here:
https://bitbucket.org/beau-barker/jsonrpcserver/src/tip/run.py

Logging
-------

To see the underlying messages going back and forth, set the logging level
to INFO.

.. sourcecode:: python

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

Issue Tracker
-------------

Issue tracker is `here
<https://bitbucket.org/beau-barker/jsonrpcserver/issues>`_.

Client
------

If you need a client, try my `jsonrpcclient
<https://pypi.python.org/pypi/jsonrpcclient>`_ library.

Todo
----

* Support `batch calls <http://www.jsonrpc.org/specification#batch>`_.

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
