jsonrpcserver
*************

Process `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

.. code-block:: python

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add
    def cube(**kwargs):
        return kwargs['num']**3

    if __name__ == '__main__':
        methods.serve_forever()

Start the server:

.. code-block:: sh

    $ pip install jsonrpcserver
    $ python server.py
     * Listening on port 5000

This example uses the built-in HTTP server, but you can process requests in any
application, (such as a Flask or Django app), by using the :mod:`dispatcher`.
The :doc:`api` has details, including :mod:`configuration <config>` of the
package. There are also examples of the dispatcher in
`Flask <https://bcb.github.io/jsonrpc/flask>`_,
`Werkzeug <https://bcb.github.io/jsonrpc/werkzeug>`_,
`ZeroMQ <https://bcb.github.io/jsonrpc/pyzmq>`_,
`Socket.io <https://bcb.github.io/jsonrpc/flask-socketio>`_, and
`http.server <https://bcb.github.io/jsonrpc/httpserver>`_.

Contribute on `Github <https://github.com/bcb/jsonrpcserver>`_.

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.io/>`_
