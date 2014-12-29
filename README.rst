jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

Simply register the `blueprint
<http://flask.pocoo.org/docs/0.10/blueprints/>`_, then dispatch the
requests to your own code.

.. sourcecode:: python

    app = Flask(__name__)
    app.register_blueprint(bp)

    # Add a route to take requests.
    @app.route('/', methods=['POST'])
    def index():
        return dispatch(HandleRequests)

    class HandleRequests:
        def add(x, y):
            return x + y

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcserver

Documentation
-------------

Documentation is available at http://jsonrpcserver.readthedocs.org/.

If you need a client, try my `jsonrpcclient
<http://jsonrpcclient.readthedocs.org/>`_ library.
