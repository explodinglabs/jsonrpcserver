jsonrpcserver
*************

Process incoming `JSON-RPC <http://www.jsonrpc.org/>`__ requests in Python 2.7
and 3.3+.

.. sourcecode:: python

    >>> from jsonrpcserver import dispatch
    >>> dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})
    {'jsonrpc': '2.0', 'result': 'meow', 'id': 1}

Full documentation is at `jsonrpcserver.readthedocs.org
<https://jsonrpcserver.readthedocs.org/>`__.
