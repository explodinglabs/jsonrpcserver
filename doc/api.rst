.. rubric:: :doc:`index`

jsonrpcserver API
*****************

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

    from jsonrpcserver.exceptions import InvalidParams
    def cube(**kwargs):
        if 'num' not in kwargs:
            raise InvalidParams('num is required')
        return kwargs['num']**3

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
