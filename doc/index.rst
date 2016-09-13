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

This example uses the built-in HTTP server, but you can process requests in any
application, (such as a Flask or Django app), by using the :mod:`dispatcher`.
The :doc:`api` has details, including :mod:`configuration <config>` of the
package. There are also :doc:`examples <examples>` of the dispatcher in http.server,
Flask, Werkzeug, ZeroMQ, Socket.IO and Tornado.

Contribute on `Github <https://github.com/bcb/jsonrpcserver>`_.

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.io/>`_
