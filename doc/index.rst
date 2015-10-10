jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
=====

Write functions that will carry out the requests, for example::

    def cat():
        return 'meow'

Then pass JSON-RPC requests to them with `dispatch() <api.html#dispatcher.dispatch>`_::

    from jsonrpcserver import dispatch
    response = dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

The return value can be used to respond to a client::

    >>> response.body
    '{"jsonrpc": "2.0", "result": "meow", "id": 1}'
    >>> response.http_status
    200

Writing the methods
===================

Example of **positional** arguments::

    def multiply(x, y):
        return x * y

    r = dispatch([multiply], {'jsonrpc': '2.0', 'method': 'multiply', 'params': [2, 3], 'id': 1})

**Keyword** arguments::

    def get_name(**kwargs):
        return kwargs['name']

    r = dispatch([get_name], {'jsonrpc': '2.0', 'method': 'get_name', 'params': {'name': 'foo'}})

.. important::

    Methods can take positional or keyword arguments, *but not both in the same
    method*. This is a `requirement
    <http://www.jsonrpc.org/specification#parameter_structures>`_  of the
    JSON-RPC specification.

If arguments are invalid, raise `InvalidParams <api.html#exceptions.InvalidParams>`_::

    from jsonrpcserver.exceptions import InvalidParams

    def get_name(**kwargs):
        if 'name' not in kwargs:
            raise InvalidParams('name is required')

    request = {'jsonrpc': '2.0', 'method': 'get_name', 'params': {}}
    response = dispatch([get_name], request)

The library catches any exception raised during dispatch, and gives the
appropriate response::

    >>> response.body
    {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params"}, "id": 1}
    >>> response.http_status
    400

Even uncaught exceptions are handled this way. This ensures we *always* have a
response for the client.

.. tip::

    More information can be found in the `body_debug
    <api.html#response.ErrorResponse.body_debug>`_ property (see the ``data``
    attribute in this response)::

        >>> r.body_debug
        {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid params", "data": "name is required"}, "id": 1}

Logging
=======

To see the JSON-RPC messages going back and forth, set the log level to
``INFO``::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)
    logging.basicConfig() # Creates a basic StreamHandler with a default format

For better logging, use custom handlers and formats::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

    # Request log
    request_handler = logging.StreamHandler()
    request_handler.setFormatter(logging.Formatter(fmt='--> %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.request').addHandler(request_handler)

    # Response log
    response_handler = logging.StreamHandler()
    response_handler.setFormatter(logging.Formatter(fmt='<-- %(http_code)d %(http_reason)s %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.response').addHandler(response_handler)

The request format has these fields:

%(message)s
    The JSON request (the body).

The response format has these fields:

%(http_code)s
    The HTTP status code one might respond with if using HTTP, eg. *400*.

%(http_reason)s
    Description of the above status code, eg. *"BAD REQUEST"*.

%(message)s
    The JSON response (the body).

Examples
========

- `HTTP Server using Flask <https://bitbucket.org/snippets/beau-barker/BAXrR/json-rpc-over-http-server-in-python>`_
- `ZeroMQ Server using PyZMQ <https://bitbucket.org/snippets/beau-barker/BAMno/json-rpc-over-zeromq-request-reply-server>`_

Links
=====

- `PyPi Package <https://pypi.python.org/pypi/jsonrpcserver>`_
- `Repository <https://bitbucket.org/beau-barker/jsonrpcserver>`_
- `Issue tracker <https://bitbucket.org/beau-barker/jsonrpcserver/issues>`_
- `Twitter @bbmelb <https://twitter.com/bbmelb>`_

See also: `jsonrpcclient <https://jsonrpcclient.readthedocs.org/>`_.
