.. rubric:: :doc:`index`

jsonrpcserver Guide
*******************

.. contents::
    :local:

Methods
=======

.. automodule:: jsonrpcserver.methods
    :exclude-members: Methods

Response
========

.. automodule:: jsonrpcserver.response
    :exclude-members: Response, ExceptionResponse, NotificationResponse,
        RequestResponse, ErrorResponse, BatchResponse, sort_response

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

To include the *"name is required"* given when the exception was raised, turn
on :mod:`debug mode <jsonrpcserver.config.debug>`.

Dispatching with context
========================

When dispatching, you may want to include some context, such as configuration
or some stateful data from the web server framework.

For this, use ``context``:

.. code-block:: python

    request = {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
    methods.dispatch(request, context={'feature_on': True})

Receiving methods should take the ``context`` value::

.. code-block:: python

    @methods.add
    def ping(context):
        ...

Asynchrony
==========

Asyncio is supported Python 3.5+, allowing requests to dispatched to
coroutines.

Usage is the same as before, however import from ``jsonrpcserver.aio``:

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
