jsonrpcserver
*************

Handle incoming `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and
3.3+.

Write functions to carry out requests:

.. sourcecode:: python

    >>> api.register_method(lambda x, y: x + y, 'add')

Then dispatch requests to them:

.. sourcecode:: python

    >>> api.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

The returned values, a JSON-RPC response and an HTTP status code, can be used to
respond to a client.

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
