jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    >>> r = dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})
    >>> r.result
    'meow'

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
