Recent Changes
==============

3.1.1 (2015-10-27)
------------------

- Notifications are no longer responded to, not even if there's an error. This
  is a `requirement <http://www.jsonrpc.org/specification#notification>`__ of
  the JSON-RPC specification. However, it can be overridden when calling
  `dispatch()
  <https://jsonrpcserver.readthedocs.org/api.html#dispatcher.dispatch>`__, to
  force notifications to receive errors.

- The HTTP status returned to notifications, which is 204 by default, can be
  `configured
  <https://jsonrpcserver.readthedocs.org/api.html#response.NotificationResponse.http_status>`__
  by monkey patching.

- Error responses can now be `configured
  <https://jsonrpcserver.readthedocs.org/api.html#exceptions>`__ by monkey
  patching.

3.1.0 (2015-10-17)
------------------

`dispatch()
<https://jsonrpcserver.readthedocs.org/api.html#dispatcher.dispatch>`__ now
accepts a dictionary of name:method pairs, as an alternative to the usual list
of methods.

3.0.0 (2015-10-11)
------------------

Major update - much of the library has been rewritten. Although it works in much
the same way as before, upgraders are advised to read the new `documentation
<http://jsonrpcserver.readthedocs.org/>`__ to pick up the changes.
