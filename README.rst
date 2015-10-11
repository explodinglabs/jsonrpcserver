jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    >>> def cat():
    ...     print('meow')
    ...
    >>> dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat'})
    'meow'

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
