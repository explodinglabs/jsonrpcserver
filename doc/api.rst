.. rubric:: :doc:`index`

jsonrpcserver API
*****************

Methods
=======

.. automodule:: jsonrpcserver.methods
    :exclude-members: Methods

Response
========

.. automodule:: jsonrpcserver.response
    :exclude-members: ExceptionResponse, NotificationResponse, RequestResponse,
        ErrorResponse, BatchResponse

Validation
==========

If arguments are unsatisfactory, raise :class:`InvalidParams
<jsonrpcserver.exceptions.InvalidParams>`:

.. code-block:: python
    :emphasize-lines: 4-5

    from jsonrpcserver.exceptions import InvalidParams

    def get(**kwargs):
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

.. automodule:: jsonrpcserver.async_methods
    :exclude-members: AsyncMethods

Configuration
=============

.. automodule:: jsonrpcserver.config

Exceptions
==========

See the :doc:`list of exceptions <exceptions>` raised by jsonrpcserver.
