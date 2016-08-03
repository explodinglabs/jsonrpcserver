"""
Exceptions are raised to return an error to the client.

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


Modify attributes to configure error responses, for example::

    from jsonrpcserver.exceptions import InvalidParams
    InvalidParams.message = 'Invalid arguments'
    InvalidParams.http_status = 406
"""

from jsonrpcserver import status

class JsonRpcServerError(Exception):
    """Base class for the other exceptions.

    :param data: Extra info (optional).
    """
    message = None

    def __init__(self, data=None):
        super(JsonRpcServerError, self).__init__(self.message)
        # Holds extra information related to the error.
        self.data = data


class ParseError(JsonRpcServerError):
    """Raised when the request is not a valid JSON object."""
    code = -32700
    message = 'Parse error'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self):
        super(ParseError, self).__init__()


class InvalidRequest(JsonRpcServerError):
    """Raised when the request is not a valid JSON-RPC object.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32600
    message = 'Invalid Request'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidRequest, self).__init__(data)


class MethodNotFound(JsonRpcServerError):
    """Raised when the method does not exist/is not available.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32601
    message = 'Method not found'
    http_status = status.HTTP_NOT_FOUND

    def __init__(self, data=None):
        super(MethodNotFound, self).__init__(data)


class InvalidParams(JsonRpcServerError):
    """Raised when invalid arguments are passed to a method, e.g. if a required
    keyword argument is missing.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32602
    message = 'Invalid params'
    http_status = status.HTTP_BAD_REQUEST

    def __init__(self, data=None):
        super(InvalidParams, self).__init__(data)


class ServerError(JsonRpcServerError):
    """Raised when there's an application specific error on the server-side.

    :param data: Extra information about the error that occurred (optional).
    """
    code = -32000
    message = 'Server error'
    http_status = status.HTTP_INTERNAL_ERROR

    def __init__(self, data=None):
        super(ServerError, self).__init__(data)
