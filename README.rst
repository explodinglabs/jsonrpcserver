jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Handles `JSON-RPC <http://www.jsonrpc.org/>`_ requests.

Write methods to carry out the requests:

.. sourcecode:: python

    >> register_jsonrpc_method('add', lambda x, y: x + y)

Then dispatch requests to them:

.. sourcecode:: python

    >> dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [2, 3], 'id': 1})
    5

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcserver

Documentation
-------------

Documentation is available at https://jsonrpcserver.readthedocs.org/.

If you need a client, try my `jsonrpcclient
<https://jsonrpcclient.readthedocs.org/>`_ library.
