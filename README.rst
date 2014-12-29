jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library has two features:

# A `Flask blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ to catch
errors, ensuring we always respond with JSON-RPC.

# A dispatcher, which validates incoming requests, passing them on to your own
code to carry out the request.

.. code-block:: python

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
