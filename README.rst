jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Handle `JSON-RPC <http://www.jsonrpc.org/>`_ requests.

First write methods to carry out the requests:

.. sourcecode:: python

    >>> from jsonrpcserver import Dispatcher
    >>> api = Dispatcher()
    >>> api.register_method(lambda x, y: x + y, 'add')

Then dispatch requests to them with ``dispatch``:

.. sourcecode:: python

    >>> request = {'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1}
    >>> api.dispatch(request)
    ({'jsonrpc': '2.0', 'result': 5, 'id': 1}, 200)

A tuple is returned with information to respond to the client with; including
the JSON-RPC response, and a recommended HTTP status code, if using HTTP for
transport.

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcserver

Documentation
-------------

Documentation is available at https://jsonrpcserver.readthedocs.org/.

If you need a client, try my `jsonrpcclient
<https://jsonrpcclient.readthedocs.org/>`_ library.
