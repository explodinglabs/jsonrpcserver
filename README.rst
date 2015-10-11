jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    from jsonrpcserver import dispatch
    def cat():
        return 'meow'
    response = dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

.. sourcecode:: python

    >>> response.result
    'meow'
    >>> response.body
    '{"jsonrpc": "2.0", "result": "meow", "id": 1}'
    >>> response.http_status
    200

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
