jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

Simply register the blueprint to your app, then write the methods to carry out
the requests:

.. sourcecode:: python

    app = Flask(__name__)
    app.register_blueprint(bp)

    class HandleRequests:
        @staticmethod
        def add(x, y):
            return x + y

    @app.route('/api', methods=['POST'])
    def index():
        return dispatch(request.get_json(), HandleRequests)

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcserver

Documentation
-------------

Documentation is available at https://jsonrpcserver.readthedocs.org/.

If you need a client, try my `jsonrpcclient
<https://jsonrpcclient.readthedocs.org/>`_ library.
