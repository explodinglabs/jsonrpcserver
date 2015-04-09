Release History
---------------

2.0.0 (2015-04-09)
^^^^^^^^^^^^^^^^^^

Major update.

**The Flask dependency has been removed.** So little of the code relied on
Flask, so that code was either updated or removed altogether. The library can
still be used with Flask with very few changes - see `flask-example.py
<https://bitbucket.org/beau-barker/jsonrpcserver/src/tip/flask-example.py>`_.

The library now works very similarly to Josh Marshall's `jsonrpclib
<https://github.com/joshmarshall/jsonrpclib>`_, but is purely for the server
side.
