Recent Changes
==============

3.1.1 (2015-10-27)
------------------

- Notifications are no longer responded to, even in the case of an error. This
  is to strictly meet the specification. However, this can be overridden when
  calling ``dispatch()``, in which case notifications will then receive errors,
  but nothing on success.

- Ability to configure the http status returned to Notifications (see
  `NotificationResponse.http_status
  <http://localhost/jsonrpcserver/api.html#response.NotificationResponse.http_status>`_).

- Error responses can now be configured by monkey patching. For example, to
  change the attributes of an "Invalid params" error:

    from jsonrpcserver.exceptions import InvalidParams
    InvalidParams.message = 'Invalid arguments'
    InvalidParams.http_status = 406

3.1.0 (2015-10-17)
------------------

`dispatch()
<https://jsonrpcserver.readthedocs.org/api.html#dispatcher.dispatch>`_ now
accepts a dictionary of name:method pairs, as an alternative to the usual list
of methods.

3.0.0 (2015-10-11)
------------------

Major update - much of the library has been rewritten. Although it works in much
the same way as before, upgraders are advised to read the new `documentation
<http://jsonrpcserver.readthedocs.org/>`_ to pick up the changes.
