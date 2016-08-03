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
    * Listening on http://localhost:5000/

This example uses the built-in HTTP server, but you can process requests in any
application, (such as a Flask or Django app), by using the :mod:`dispatcher`.

Dispatcher
==========

.. automodule:: dispatcher

Methods
-------

.. automodule:: methods
    :exclude-members: Methods

Response
--------

.. automodule:: response
    :exclude-members: ExceptionResponse, NotificationResponse, RequestResponse,
        ErrorResponse, BatchResponse

Validation
==========

If arguments are unsatisfactory, raise :class:`InvalidParams
<jsonrpcserver.exceptions.InvalidParams>`:

.. code-block:: python
    :emphasize-lines: 3-4

    >>> from jsonrpcserver.exceptions import InvalidParams
    >>> def cube(**kwargs):
    ...     if 'num' not in kwargs:
    ...         raise InvalidParams('num is required')
    ...     return kwargs['num']**3

The dispatcher catches the exception and gives the appropriate response:

.. code-block:: python

    >>> dispatch([cube], {'jsonrpc': '2.0', 'method': 'cube', 'params': {}, 'id': 1})
    {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}

To include the *"num is required"* message given when the exception was raised,
turn on :mod:`debug mode <config.debug>`.

Configuration
=============

.. automodule:: config

Exceptions
==========

See the :doc:`list of exceptions <exceptions>` raised by jsonrpcserver.

Examples
========

See code snippets making use of jsonrpcserver in
`Flask <https://bcb.github.io/jsonrpc/flask>`_,
`Werkzeug <https://bcb.github.io/jsonrpc/werkzeug>`_,
`ZeroMQ <https://bcb.github.io/jsonrpc/pyzmq>`_,
`Socket.io <https://bcb.github.io/jsonrpc/flask-socketio>`_, and
`http.server <https://bcb.github.io/jsonrpc/httpserver>`_.

Contribute on `Github <https://github.com/bcb/jsonrpcserver>`_.

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.io/>`_
