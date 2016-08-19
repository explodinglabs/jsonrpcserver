jsonrpcserver
*************

Process `JSON-RPC <http://www.jsonrpc.org/>`__ requests in Python 2.7 and 3.3+.

.. sourcecode:: python

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    if __name__ == '__main__':
        methods.serve_forever()

Full documentation is at `jsonrpcserver.readthedocs.io
<https://jsonrpcserver.readthedocs.io/>`__.
