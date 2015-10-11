jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    from jsonrpcserver import dispatch
    def cat():
        return 'meow'
    r = dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

Full documentation is available at https://jsonrpcserver.readthedocs.org/.
