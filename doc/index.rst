jsonrpcserver
*************

Process `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and
3.3+.

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
=====

Write methods to carry out requests. Here we simply cube a number:

.. code-block:: python

    >>> def cube(**kwargs):
    ...     return kwargs['num']**3

Dispatch JSON-RPC requests to the methods:

.. code-block:: python

    >>> from jsonrpcserver import dispatch
    >>> dispatch([cube], {'jsonrpc': '2.0', 'method': 'cube', 'params': {'num': 3}, 'id': 1})
    {'jsonrpc': '2.0', 'result': 27, 'id': 1}

If arguments are unsatisfactory, raise :class:`InvalidParams
<jsonrpcserver.exceptions.InvalidParams>` in your method:

.. code-block:: python
    :emphasize-lines: 3-4

    >>> from jsonrpcserver.exceptions import InvalidParams
    >>> def cube(**kwargs):
    ...     if 'num' not in kwargs:
    ...         raise InvalidParams('num is required')
    ...     return kwargs['num']**3

The library catches the exception and gives the appropriate response:

.. code-block:: python

    >>> dispatch([cube], {'jsonrpc': '2.0', 'method': 'cube', 'params': {}, 'id': 1})
    {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}

To include the *"num is required"* message given when the exception was raised,
turn on debug mode:

.. code-block:: python

    >>> from jsonrpcserver import config
    >>> config.debug = True
    >>> dispatch([cube], {'jsonrpc': '2.0', 'method': 'cube', 'params': {}, 'id': 1})
    {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params', 'data': 'num is required'}, 'id': 1}

Note the extra 'data' key in the response.

You can also raise :class:`ServerError <jsonrpcserver.exceptions.ServerError>`
to let the client know there was an error on the server side.

If you're processing HTTP requests, an ``http_status`` attribute can be used
when responding to the client:

.. code-block:: python

    >>> r = dispatch([cube], {})
    >>> r
    {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None}
    >>> r.http_status
    400

.. automodule:: config

Logging
=======

To see the JSON-RPC messages going back and forth, set the logging level to
``INFO`` and add a basic handler::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)
    logging.getLogger('jsonrpcserver').addHandler(logging.StreamHandler())

Alternatively, use a custom log format::

    request_format = '--> %(message)s'
    response_format = '<-- %(http_code)d %(http_reason)s %(message)s'

    request_handler = logging.StreamHandler()
    request_handler.setFormatter(logging.Formatter(fmt=request_format))
    logging.getLogger('jsonrpcserver.dispatcher.request').addHandler(
        request_handler)

    response_handler = logging.StreamHandler()
    response_handler.setFormatter(logging.Formatter(fmt=response_format))
    logging.getLogger('jsonrpcserver.dispatcher.response').addHandler(
        response_handler)

The request format has these fields:

:message: The JSON request (the body).

The response format has these fields:

:http_code: The recommended HTTP status code, if using HTTP, eg. *400*.
:http_reason: Description of the above HTTP status code, eg. *"BAD REQUEST"*.
:message: The JSON response (the body).

Examples
========

- `HTTP Server using Werkzeug <https://bcb.github.io/jsonrpc/werkzeug>`_
- `HTTP Server using Flask <https://bcb.github.io/jsonrpc/flask>`_
- `HTTP Server using Python's http.server module <https://bcb.github.io/jsonrpc/httpserver>`_
- `ZeroMQ Server using PyZMQ <https://bcb.github.io/jsonrpc/pyzmq>`_
- `Socket.IO Server using Flask-SocketIO <https://bcb.github.io/jsonrpc/flask-socketio>`_

Links
=====

- `Github <https://github.com/bcb/jsonrpcserver>`_
- `Issues <https://github.com/bcb/jsonrpcserver/issues>`_
- `PyPi <https://pypi.python.org/pypi/jsonrpcserver>`_
- `Twitter @bbmelb <https://twitter.com/bbmelb>`_

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.io/>`_
