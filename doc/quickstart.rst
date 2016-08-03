.. rubric:: :doc:`index`

Quickstart
**********

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
=====

Configuration
=============

See the :mod:`config <config>` api for how to configure various options.

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

:doc:`Back home <index>`
