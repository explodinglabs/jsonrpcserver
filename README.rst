jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    >>> response = dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})
    >>> response.body
    {'jsonrpc': '2.0', 'result': 'meow', 'id': 1}

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
