jsonrpcserver
*************

Process `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. code-block:: python

    from jsonrpcserver import Methods

    methods = Methods()
    @methods.add
    def ping():
        return 'pong'

    if __name__ == '__main__':
        methods.serve_forever()

Start the server:

.. code-block:: sh

    $ pip install jsonrpcserver
    $ python server.py
     * Listening on port 5000

This example uses the built-in server, but you can process requests in any
application, (such as a Flask or Django app), by using the :mod:`dispatcher`.
See :doc:`examples <examples>` of usage in various frameworks. The :doc:`api`
has details, including :mod:`configuration <config>` of the package.

Contribute on `Github <https://github.com/bcb/jsonrpcserver>`_.

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.io/>`_
