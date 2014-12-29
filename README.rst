jsonrpcserver
=============

.. image:: https://pypip.in/v/jsonrpcserver/badge.png
.. image:: https://pypip.in/d/jsonrpcserver/badge.png

Receive `JSON-RPC <http://www.jsonrpc.org/>`_ requests in a `Flask
<http://flask.pocoo.org/>`_ app.

The library has two features:

#. A dispatcher, which validates incoming requests and then passes them on to
   your own code to carry out the request.

#. A `Flask blueprint <http://flask.pocoo.org/docs/0.10/blueprints/>`_ to catch
   errors, ensuring we always respond with JSON-RPC.

Installation
------------

.. sourcecode:: sh

    $ pip install jsonrpcclient

Documentation
-------------

Documentation is available at http://jsonrpcclient.readthedocs.org/.
