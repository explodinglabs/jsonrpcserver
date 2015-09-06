jsonrpcserver
*************

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests in Python 2.7 and 3.3+.

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Usage
=====

Write functions to carry out the requests::

    >>> from jsonrpcserver import Dispatcher
    >>> dispatcher = Dispatcher()
    >>> dispatcher.register_method(lambda x, y: x + y, 'add')

You may prefer the decorator syntax::

    >>> @dispatcher.method('add')
    ... def add(x, y):
    ...     return x + y

Keyword parameters are also acceptable::

    >>> @dispatcher.method('find')
    ... def find(**kwargs):
    ...     name = kwargs['name']

.. important::

    Use either positional or keyword parameters, but not both in the same
    method. This is a requirement of the `JSON-RPC specs
    <http://www.jsonrpc.org/specification#parameter_structures>`_.

Dispatching
-----------

Dispatch requests with ``dispatch()``::

    >>> dispatcher.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

.. tip::

    ``dispatch()`` takes a dictionary. If you have a string, use ``dispatch_str()``.

The returned values, a JSON-RPC response and an HTTP status code, can be used to
respond to a client.

Exceptions
==========

On receiving invalid arguments, raise ``InvalidParams``::

    from jsonrpcserver.exceptions import InvalidParams, ServerError

    @dispatcher.method('find')
    def find(**kwargs):
        """Find a customer."""
        # Required params
        try:
            firstname = kwargs['firstname']
            lastname = kwargs['lastname']
        except KeyError as e:
            raise InvalidParams(str(e))
        # Optional params
        age = kwargs.get('age')

The library will catch the exception and return the correct JSON-RPC error
response:

.. code-block:: javascript

    ({"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid params"}, "id": 1}, 400)

To notify the client of a server-side error, raise ``ServerError``::

    try:
        db.session.commit()
    except SQLAlchemyError as e:
        raise ServerError(str(e))

The library will take care of it, returning:

.. code-block:: javascript

    ({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error"}, "id": 1}, 500)

Debugging
=========

In the above exceptions, extra debugging information is included when raising
the exceptions. To include this extra information in the JSON-RPC responses,
enable debugging (pass ``debug=True`` when instantiating the dispatcher). The
extra info will then be included in the ``data`` property, like this::

    >>> dispatcher.debug = True
    >>> dispatcher.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {'id': 1}, 'id': 1})
    ({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "Column 'id' does not exist"}, "id": 1}, 500)

Logging
=======

The JSON-RPC messages are logged on the ``INFO`` log level. To see them::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

    logging.basicConfig() # Creates a basic StreamHandler with a default format

For better logging, use custom handlers and formats::

    import logging
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

    request_handler = logging.StreamHandler()
    request_handler.setFormatter(logging.Formatter(fmt='--> %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.request').addHandler(request_handler)

    response_handler = logging.StreamHandler()
    response_handler.setFormatter(logging.Formatter(fmt='<-- %(http_code)d %(http_reason)s %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.response').addHandler(response_handler)

The request format has these fields:

%(message)s
    The JSON request (the body).

The response format has these fields:

%(http_code)s
    The HTTP status code received from the server, eg. *400*.

%(http_reason)s
    The description of the status code, eg. *"BAD REQUEST"*.

%(message)s
    The JSON response (the body).

Examples
========

- `HTTP Server using Flask <https://bitbucket.org/snippets/beau-barker/BAXrR/json-rpc-over-http-server-in-python>`_
- `ZeroMQ Server using pyzmq <https://bitbucket.org/snippets/beau-barker/BAMno/json-rpc-over-zeromq-request-reply-server>`_

Links
=====

- PyPi Package: https://pypi.python.org/pypi/jsonrpcserver
- Repository: https://bitbucket.org/beau-barker/jsonrpcserver
- Issue tracker: https://bitbucket.org/beau-barker/jsonrpcserver/issues

Need a client? Try my `jsonrpcclient <https://jsonrpcclient.readthedocs.org/>`_
library.
