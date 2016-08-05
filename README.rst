jsonrpcserver
*************

Process `JSON-RPC <http://www.jsonrpc.org/>`__ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    >>> from jsonrpcserver import Methods
    >>> methods = Methods()
    >>> methods.add(lambda: 'pong', 'ping')
    >>> methods.serve_forever()
     * Listening on port 5000

Full documentation is at `jsonrpcserver.readthedocs.io
<https://jsonrpcserver.readthedocs.io/>`__.
