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
        RequestResponse, ErrorResponse, BatchResponse

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

Asynchronous
============

Starting from jsonrpcserver v3.4 you can dispatch to coroutines (in Python
3.5+). Usage is the same as before, but import from ``jsonrpcserver.aio``:

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
