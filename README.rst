jsonrpcserver
*************

.. image:: https://drone.io/bitbucket.org/beau-barker/jsonrpcserver/status.png

Process incoming `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7
and 3.3+.

.. sourcecode:: python

    >>> dispatch([cat, dog], {'jsonrpc': '2.0', 'method': 'cat'})
    'meow'

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
