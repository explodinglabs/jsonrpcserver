jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests.

Write methods to carry out the requests:

.. sourcecode:: python

    >>> api.register_method(lambda x, y: x + y, 'add')

Then dispatch requests to them:

.. sourcecode:: python

    >>> api.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

A tuple is returned with some information to respond to the client with. This
includes a JSON-RPC response and a HTTP status code if needed.

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
