.. rubric::
    `jsonrpcserver <index.html>`_

Quickstart
**********

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
=====

Write functions that will carry out the requests, for example::

    def cat():
        return 'meow'

Then pass JSON-RPC requests to them with `dispatch()
<api.html#dispatcher.dispatch>`_::

    from jsonrpcserver import dispatch
    response = dispatch([cat], {'jsonrpc': '2.0', 'method': 'cat', 'id': 1})

The first argument is the list of methods that can be called. The second
argument is the request itself.

The return value can be used to respond to a client::

    >>> response.body
    '{"jsonrpc": "2.0", "result": "meow", "id": 1}'
    >>> response.http_status
    200

Writing the methods
===================

Example of positional arguments::

    def multiply(x, y):
        return x * y

    request = {'jsonrpc': '2.0', 'method': 'multiply', 'params': [2, 3], 'id': 1}
    response = dispatch([multiply], request)

Keyword arguments::

    def get_name(**kwargs):
        return kwargs['name']

    request = {'jsonrpc': '2.0', 'method': 'get_name', 'params': {'name': 'foo'}, 'id': 1}
    response = dispatch([get_name], request)

.. important::

    Use positional or keyword arguments, *but not both in the same method*.
    This is a `requirement
    <http://www.jsonrpc.org/specification#parameter_structures>`_  of the
    JSON-RPC specification.

Responding to the client
------------------------

To send payload data back in the response message, simply ``return`` it from the
method as shown above. Any string, number, list or dictionary is fine.

Sending an Error response
-------------------------

The library automatically handles some client errors, but there are other times
where we need to inform the client of an error. This is done by raising an
exception.

For example, if you're unhappy with the arguments received, raise `InvalidParams
<api.html#exceptions.InvalidParams>`_::

    from jsonrpcserver.exceptions import InvalidParams

    def get_name(**kwargs):
        if 'name' not in kwargs:
            raise InvalidParams('name is required')

    request = {'jsonrpc': '2.0', 'method': 'get_name', 'params': {}, 'id': 1}
    response = dispatch([get_name], request)

The library catches the exception and gives the appropriate response::

    >>> response.body
    {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params"}, "id": 1}
    >>> response.http_status
    400

There's also `ServerError <api.html#exceptions.InvalidParams>`_, which lets the
client know of a problem at the application end. In fact, any other exceptions
raised will result in a *"Server error"* response::

    def divide_by_zero(**kwargs):
        1/0

    request = {'jsonrpc': '2.0', 'method': 'divide_by_zero', 'id': 1}
    response = dispatch([divide_by_zero], request)

::

    >>> response.body
    {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Server error"}, "id": 1}
    >>> response.http_status
    500

This ensures we *always* have a response for the client.

.. tip::

    The `body_debug <api.html#response.ErrorResponse.body_debug>`_ property
    gives further details about an error, in the ``data`` attribute::

        >>> response.body_debug
        {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Server error", "data": "divide by zero"}, "id": 1}

Logging
=======

To see the JSON-RPC messages going back and forth, set the log level to
``INFO``::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

Then create a basic handler::

    logging.basicConfig() # Creates a StreamHandler with a default format

Or use custom handlers and formats::

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

%(message)s
    The JSON request (the body).

The response format has these fields:

%(http_code)s
    The recommended HTTP status code, if using HTTP, eg. *400*.

%(http_reason)s
    Description of the above HTTP status code, eg. *"BAD REQUEST"*.

%(message)s
    The JSON response (the body).

Examples
========

- `HTTP Server <https://bitbucket.org/snippets/beau-barker/BAXrR/json-rpc-over-http-server-in-python>`_  using Flask
- `ZeroMQ Server <https://bitbucket.org/snippets/beau-barker/BAMno/json-rpc-over-zeromq-request-reply-server>`_ using PyZMQ
