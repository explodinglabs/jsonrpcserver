jsonrpcserver
*************

Takes `JSON-RPC <http://www.jsonrpc.org/>`_ requests and passes them on to your
own methods.

Installation
============

.. code-block:: sh

    $ pip install jsonrpcserver

Writing the methods
===================

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
    method. This is a requirement of the JSON-RPC `specs
    <http://www.jsonrpc.org/specification#parameter_structures>`_.

Dispatching to your methods
===========================

Pass requests through ``dispatch()``::

    >>> dispatcher.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

``dispatch()`` takes a dict. If you have a string, convert it to dict first.

The returned values - a JSON-RPC response and an HTTP status code - can be
used to respond to a client.

Exceptions
==========

When your receive invalid arguments, raise ``InvalidParams``::

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

In the above exceptions, potentially sensitive information is included when
raising the exception, which can help with debugging. This is not included in
the response by default. To include the extra information, add
``more_info=True`` when calling ``dispatch()``. The extra info will be included
in the ``data`` property, like::

    >>> dispatcher.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {'id': 1}, 'id': 1}, more_info=True)
    ({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "Column 'id' does not exist"}, "id": 1}, 500)

Logging
=======

To see the json messages being passed back and forth, set the log level to
INFO::

    import logging
    logging.basicConfig()
    logging.getLogger('jsonrpcserver').setLevel(logging.INFO)

For better logging, replace ``basicConfig`` with your own handlers, and
customize the log format for ``jsonrpcserver.dispatcher.request`` and
``jsonrpcserver.dispatcher.response``::

    request_handler = logging.StreamHandler()
    request_handler.setFormatter(logging.Formatter(fmt='--> %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.request').addHandler(request_handler)

    response_handler = logging.StreamHandler()
    response_handler.setFormatter(logging.Formatter(fmt='<-- %(http_code)d %(http_reason)s %(message)s'))
    logging.getLogger('jsonrpcserver.dispatcher.response').addHandler(response_handler)

The request format has these fields:

%(message)s
    The json request (the body).

The response format has these fields:

%(http_code)s
    The HTTP status code received from the server, eg. *400*.

%(http_reason)s
    The description of the status code, eg. *"BAD REQUEST"*.

%(message)s
    The json response (the body).

Links
=====

- PyPi Package: https://pypi.python.org/pypi/jsonrpcserver
- Repository: https://bitbucket.org/beau-barker/jsonrpcserver
- Issue tracker: https://bitbucket.org/beau-barker/jsonrpcserver/issues

If you need a client, try my `jsonrpcclient
<https://jsonrpcclient.readthedocs.org/>`_ library.
