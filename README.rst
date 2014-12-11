jsonrpcserver
=============

Allows you to take `JSON-RPC 2.0 <http://www.jsonrpc.org/>`_ requests in a
`Flask <http://flask.pocoo.org/>`_ app.

It has two features:

#. A ``dispatch`` method for handling requests, passing the details on to your
   own functions to carry out the request.

#. A `blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ for handling
   errors, ensuring we *always* respond with json.


Installation
------------

    pip install jsonrpcserver


Usage
-----

Register the blueprint to your app:

.. sourcecode:: python

    import sys
    from flask import Flask
    from jsonrpcserver import bp, dispatch, exceptions

    # Create a flask app and register the blueprint.
    app = Flask(__name__)
    app.register_blueprint(bp)


Create a route for access, and call ``dispatch``:

.. sourcecode:: python

    @app.route('/', methods=['POST'])
    def index():
        return dispatch(sys.modules[__name__])

The argument to ``dispatch`` can be any object containing methods that will
carry out the requests. Here I've used this very module so we can write the
methods right here.

Now write the request handling methods, as you would any other Python function:

.. sourcecode:: python

    def add(num1, num2):
        return num1 + num2

You can take any number of positional or keyword arguments.

.. sourcecode:: python

    def find(name, age=42, *args, **kwargs):
        pass

When arguments are invalid, raise ``InvalidParams``:

.. sourcecode:: python

    def add(num1, num2='Not a number'):
        try:
            return num1 + num2
        except TypeError as e:
            raise exceptions.InvalidParams(str(e))

The underlying messages being transferred are logged to the INFO log level. To
see them, set the logging level to INFO:

``import logging; logging.getLogger('jsonrpcclient').setLevel(logging.INFO)``

See it all put together, go `here
<https://bitbucket.org/beau-barker/jsonrpcserver/run.py>`_.

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
