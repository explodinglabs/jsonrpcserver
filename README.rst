jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library stays out of your way, having just two features; a dispatcher to
validate requests and pass them onto your code, and a `blueprint
<http://flask.pocoo.org/docs/0.10/blueprints/>`_ to handle errors.

.. sourcecode:: python

    # Create an app and register the blueprint
    app = Flask(__name__)
    app.register_blueprint(bp)

    # Dispatch incoming requests
    @app.route('/', methods=['POST'])
    def index():
        return dispatch(HandleRequests)

    class HandleRequests:
        def add(x, y):
            return x + y

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcclient

Documentation
-------------

Documentation is available at http://jsonrpcclient.readthedocs.org/.
