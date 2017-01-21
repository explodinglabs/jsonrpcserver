.. rubric:: :doc:`index`

jsonrpcserver Examples
**********************

Showing how to take JSON-RPC requests in various frameworks and transport
protocols.

.. contents::
    :local:

aiohttp
=======

::

    $ pip install jsonrpcserver aiohttp

.. literalinclude:: ../examples/aiohttp_server.py

See `blog post <https://bcb.github.io/jsonrpc/aiohttp>`__.

Django
======

Create a ``views.py``:

.. literalinclude:: ../examples/django_server.py

See `blog post <https://bcb.github.io/jsonrpc/django>`__.

Flask
=====

::

    $ pip install jsonrpcserver flask

.. literalinclude:: ../examples/flask_server.py

See `blog post <https://bcb.github.io/jsonrpc/flask>`__.

http.server
===========

Python's built-in `http.server
<https://docs.python.org/3/library/http.server.html>`__ module.

::

    $ pip install jsonrpcserver

.. literalinclude:: ../examples/http_server.py

See `blog post <https://bcb.github.io/jsonrpc/httpserver>`__.

Plain jsonrpcserver
===================

Using jsonrpcserver's built-in ``serve_forever`` method.

::

    $ pip install jsonrpcserver

The quickest way to serve a method::

    from jsonrpcserver import Methods
    Methods(ping=lambda:'pong').serve_forever()

Using the ``@add`` decorator:

.. literalinclude:: ../examples/jsonrpcserver_server.py

Socket.IO
=========

::

    $ pip install jsonrpcserver flask flask-socketio eventlet

.. literalinclude:: ../examples/socketio_server.py

See `blog post <https://bcb.github.io/jsonrpc/flask-socketio>`__.

Tornado
=======

::

    $ pip install jsonrpcserver tornado

.. literalinclude:: ../examples/tornado_server.py

See `blog post <https://bcb.github.io/jsonrpc/tornado>`__.

Websockets
==========

::

    $ pip install jsonrpcserver websockets

.. literalinclude:: ../examples/websockets_server.py

See `blog post <https://bcb.github.io/jsonrpc/websockets>`__.

Werkzeug
========

::

    $ pip install jsonrpcserver werkzeug

.. literalinclude:: ../examples/werkzeug_server.py

See `blog post <https://bcb.github.io/jsonrpc/werkzeug>`__.

ZeroMQ
======

::

    $ pip install jsonrpcserver pyzmq

.. literalinclude:: ../examples/zeromq_server.py

See `blog post <https://bcb.github.io/jsonrpc/zeromq>`__.

ZeroMQ (asynchronous)
=====================

::

    $ pip install jsonrpcserver aiozmq

.. literalinclude:: ../examples/aiozmq_server.py

See `blog post <https://bcb.github.io/jsonrpc/zeromq-async>`__.
