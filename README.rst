jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library has two features: a dispatcher to validate requests and pass them
onto your code, and a `blueprint
<http://flask.pocoo.org/docs/0.10/blueprints/>`_ to handle errors.

.. sourcecode:: python

    from flask import Flask
    from jsonrpcserver import bp, dispatch, exceptions

    app = Flask(__name__)
    app.register_blueprint(bp)

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
