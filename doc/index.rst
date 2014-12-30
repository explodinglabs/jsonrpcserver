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

    from flask import Flask
    from jsonrpcserver import bp, dispatch, exceptions

    app = Flask(__name__)
    app.register_blueprint(bp)

Add a route to pass requests on to your handling methods::

    @app.route('/', methods=['POST'])
    def index():
        return dispatch(HandleRequests)

Now go ahead and write the methods that will carry out the requests::

    class HandleRequests:

        @staticmethod
        def add(x, y):
            """Add two numbers."""
            return x + y

Keyword arguments are also acceptable::

    @staticmethod
    def find(**kwargs):
        """Find a customer."""
        # Optional parameters
        name = kwargs.get('name', None)

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
            # Required parameters
            firstname = kwargs['firstname']
            lastname = kwargs['lastname']
        except KeyError as e:
            raise exceptions.InvalidParams(str(e))

The blueprint will catch the exception, and return the correct error response
to the client:

.. code-block:: javascript

    {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params", "data": "Key error: 'firstname'"}, "id": 1}

To return a custom error in your app, raise ``ServerError``::

    try:
        db.session.commit()
    except SQLAlchemyError:
        raise exceptions.ServerError('Database error')

The blueprint will take care of it:

.. code-block:: javascript

    {"jsonrpc": "2.0", "error": {"code": -32000, "message": "Database error"}, "id": 1}


Logging
^^^^^^^

To see the underlying messages going back and forth, set the logging level
to INFO::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

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
