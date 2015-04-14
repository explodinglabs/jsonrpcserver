jsonrpcserver
=============

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests.

Takes JSON-RPC requests and passes them on to your own methods.

Installation
------------

.. code-block:: sh

    $ pip install jsonrpcserver

Writing the methods
-------------------

Write functions to carry out the requests::

    >>> from jsonrpcserver import Dispatcher
    >>> api = Dispatcher()
    >>> api.register_method(lambda x, y: x + y, 'add')

You may prefer use the decorator syntax::

    >>> @api.method('add')
    ... def add(x, y):
    ...     return x + y

Keyword parameters are also acceptable::

    >>> @api.method('find')
    ... def find(**kwargs):
    ...     name = kwargs['name']

.. important::

    Use either positional or keyword parameters, but not both in the same
    method - as required by the `JSON-RPC specs
    <http://www.jsonrpc.org/specification#parameter_structures>`_.

Dispatching to your methods
---------------------------

Dispatch requests to your methods with ``dispatch``::

    >>> api.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

The returned values - a JSON-RPC response and an HTTP status code - can be
used to respond to a client.

Exceptions
----------

When arguments to your methods are invalid, raise ``InvalidParams``::

    from jsonrpcserver.exceptions import InvalidParams, ServerError

    @api.method('find')
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

The library will take care of it:

.. code-block:: javascript

    ({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error"}, "id": 1}, 500)

Debugging
~~~~~~~~~

In the above exceptions, we're passing more information to the exceptions than
what is appearing in the error response. To see the extra information in the
error response, pass ``more_info=True`` to the dispatch method. You'll get an
extra 'data' value in the errors, something like::

    >>> api.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {'id': 1}, 'id': 1}, more_info=True)
    ({"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "Column 'id' does not exist"}, "id": 1}, 500)

Logging
-------

To give fine control, two loggers are used; ``request_log`` for requests and
``response_log`` for responses. These do nothing until they're set up. The
following shows how to output the ``request_log`` to stderr::

    from logging import StreamHandler, Formatter, INFO
    from jsonrpcserver import request_log, response_log

    # Json messages are on the INFO log level.
    request_log.setLevel(INFO)

    # Add a stream handler to output to stderr.
    request_handler = StreamHandler()
    request_log.addHandler(request_handler)

Do the same with ``response_log`` to see the responses::

    response_log.setLevel(INFO)
    response_handler = StreamHandler()
    response_log.addHandler(response_handler)

For better log entries, customize the log format::

    # Set a custom request log format
    request_format = Formatter(fmt='--> %(message)s')
    request_handler.setFormatter(request_format)

    # Set a custom response log format
    response_format = Formatter(fmt='<-- %(http_code)d %(http_reason)s %(message)s')
    response_handler.setFormatter(response_format)

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


Clients
-------

Python
~~~~~~

Try my `jsonrpcclient <https://jsonrpcclient.readthedocs.org/>`_ library.

.. sourcecode:: python

    >>> from jsonrpcclient import Server
    >>> s = Server('http://example.com/api')
    >>> s.request('add', 2, 3)
    5

curl
~~~~

.. code-block:: sh

    $ curl -X POST -H 'Content-type: application/json' -d '{"jsonrpc": "2.0", "method": "add", "params": [2, 3], "id": 1}' http://example.com/api

jQuery
~~~~~~

.. code-block:: javascript

  $.ajax({
    type: 'POST',
    url: '/api',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json'
    },
    data: JSON.stringify({
      jsonrpc: '2.0',
      method: 'add',
      params: [2, 3],
      id: 1
    })
  })
  .done(function(data) {
    $('#answer').html(data.result);
  });

Todo
----

* Support `batch calls <http://www.jsonrpc.org/specification#batch>`_.

Links
-----

* Package: https://pypi.python.org/pypi/jsonrpcserver
* Repository: https://bitbucket.org/beau-barker/jsonrpcserver
* Issue tracker: https://bitbucket.org/beau-barker/jsonrpcserver/issues
