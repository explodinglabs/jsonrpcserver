jsonrpcserver
=============

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library has two features:

#. A dispatcher, which validates incoming requests and passes them on to your
   own code to carry out the request.

#. A `Flask blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ to catch
   errors, ensuring we always respond with JSON-RPC.

Installation
------------

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
-----

Create a Flask app and register the blueprint::

    from flask import Flask, request
    from jsonrpcserver import bp, dispatch, exceptions

    app = Flask(__name__)
    app.register_blueprint(bp)

Add a route to pass requests on to your handling methods::

    @app.route('/', methods=['POST'])
    def index():
        return dispatch(flask.request.get_json(), HandleRequests)

Now go ahead and write the methods that will carry out the requests::

    class HandleRequests:

        @staticmethod
        def add(x, y):
            """Add two numbers."""
            return x + y

Keyword parameters are also acceptable::

    @staticmethod
    def find(**kwargs):
        """Find a customer."""
        name = kwargs.get('name')

.. important::

    Use either positional or keyword parameters, but not both in the same
    method. See `Parameter Structures
    <http://www.jsonrpc.org/specification#parameter_structures>`_ in the
    JSON-RPC specification.

See it all put together `here
<https://bitbucket.org/beau-barker/jsonrpcserver/src/tip/run.py>`_.

Exceptions
^^^^^^^^^^

When arguments are invalid, raise ``InvalidParams``::

    def find(**kwargs):
        """Find a customer."""
        try:
            firstname = kwargs['firstname']
            lastname = kwargs['lastname']
        except KeyError as e:
            raise exceptions.InvalidParams(str(e))

The blueprint will catch the exception and return the correct error response to
the client:

.. code-block:: javascript

    {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": "Key error: 'firstname'"}, "id": 1}

To notify the client of some other error, raise ``ServerError``::

    try:
        db.session.commit()
    except SQLAlchemyError:
        raise exceptions.ServerError('Database error')

The blueprint will take care of it:

.. code-block:: javascript

    {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Database error"}, "id": 1}


Logging
^^^^^^^

To give fine control, two loggers are used; ``request_log`` for requests and
``response_log`` for responses. These do nothing until they're set up. The
following shows how to output the ``request_log`` to stderr::

    from logging import StreamHandler, Formatter, INFO
    from jsonrpcserver import request_log, response_log

    # Json messages are on the INFO log level.
    request_log.setLevel(INFO)

    # Add a stream handler to output to stderr.
    request_handler = StreamHandler()
    request_log.addHandler(request_handler)

Do the same with ``response_log`` to see the responses::

    response_log.setLevel(INFO)
    response_handler = StreamHandler()
    response_log.addHandler(response_handler)

For better log entries, customize the log format::

    # Set a custom request log format
    request_format = Formatter(fmt='--> %(message)s')
    request_handler.setFormatter(request_format)

    # Set a custom response log format
    response_format = Formatter(fmt='<-- %(http_code)d %(http_reason)s %(message)s')
    response_handler.setFormatter(response_format)

The request format has these fields:

%(http_headers)s
    The full HTTP headers.

%(message)s
    The json request (the body).

The response format has these extra fields:

%(http_code)s
    The HTTP status code received from the server, eg. *400*.

%(http_reason)s
    The description of the status code, eg. *"BAD REQUEST"*.

%(http_headers)s
    The full HTTP headers.

%(message)s
    The json response (the body).


Todo
----

* Support `batch calls <http://www.jsonrpc.org/specification#batch>`_.

Links
-----

* Package: https://pypi.python.org/pypi/jsonrpcserver
* Repository: https://bitbucket.org/beau-barker/jsonrpcserver
* Issue tracker: https://bitbucket.org/beau-barker/jsonrpcserver/issues

If you need a client, try my `jsonrpcclient
<https://jsonrpcclient.readthedocs.org/>`_ library.
