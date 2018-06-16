.. rubric:: :doc:`index`

jsonrpcserver Guide
*******************

.. contents::
    :local:

Methods
=======

.. automodule:: jsonrpcserver.methods
    :exclude-members: Methods

Dispatching
===========

Dispatch a JSON-RPC request::

    >>> response = methods.dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    --> {"jsonrpc": "2.0", "method": "ping", "id": 1}
    <-- {"jsonrpc": "2.0", "result": "pong", "id": 1}

You may want to include some configuration or data from a web server framework;
for this, use ``context``:

.. code-block:: python

    methods.dispatch(request, context={'feature_enabled': True})

The receiving methods should take the ``context`` value:

.. code-block:: python

    @methods.add
    def ping(context):
        ...

Response
========

The return value from ``dispatch`` is a response object.

::

    >>> response = methods.dispatch(request)
    >>> response
    {'jsonrpc': '2.0', 'result': 'foo', 'id': 1}

Use ``str()`` to get a JSON-encoded string::

    >>> str(response)
    '{"jsonrpc": "2.0", "result": "foo", "id": 1}'

There's also an HTTP status code if you need it::

    >>> response.http_status
    200

Validation
==========

If arguments are unsatisfactory, raise :class:`InvalidParams
<jsonrpcserver.exceptions.InvalidParams>`:

.. code-block:: python

    from jsonrpcserver.exceptions import InvalidParams

    @methods.add
    def get_customer(**kwargs):
        if 'name' not in kwargs:
            raise InvalidParams('name is required')

The dispatcher catches the exception and gives the appropriate response:

.. code-block:: python

    >>> methods.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {}, 'id': 1})
    {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}

To include the *"name is required"* given when the exception was raised, turn on
:mod:`debug mode <jsonrpcserver.config.debug>`.

Asynchrony
==========

Asyncio is supported Python 3.5+, allowing requests to be dispatched to coroutines.

Usage is the same as before, however import methods from ``jsonrpcserver.aio``:

.. code-block:: python

    from jsonrpcserver.aio import methods

    @methods.add
    async def ping():
        return await some_long_running_task()

Then ``await`` the dispatch:

.. code-block:: python

    response = await methods.dispatch(request)

Configuration
=============

.. automodule:: jsonrpcserver.config

Exceptions
==========

See the :doc:`list of exceptions <exceptions>` raised by jsonrpcserver.
