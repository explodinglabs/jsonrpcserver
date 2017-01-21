.. rubric:: :doc:`index`

Exceptions
**********

The full list of exceptions raised by ``dispatch()`` is listed below.
Attributes can be changed to configure error responses, for example::

    from jsonrpcserver.exceptions import InvalidParams
    InvalidParams.message = 'Invalid arguments'
    InvalidParams.http_status = 406

.. automodule:: jsonrpcserver.exceptions
    :exclude-members: JsonRpcServerError
