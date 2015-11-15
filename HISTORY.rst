Recent Changes
==============

3.2.0 (15 Nov 2015)
-------------------

- Now accepts `batch requests <http://www.jsonrpc.org/specification#batch>`.

- ``dispatch()`` now returns a JSON-RPC response object. Previously this was
  accessed in the ``json`` attribute. Now just access parts of the response
  directly, (like ``response['result']``).  Accordingly, **most of the
  attributes have been removed**:
  
  - ``result`` (use ``response['result']``),
  - ``request_id`` (use ``response['id']``),
  - ``body`` (use ``str(response)``),
  - ``body_debug`` (`enable debugging
    <http://jsonrpcserver.readthedocs.org/api.html#response.ErrorResponse>`__
    and use ``str(response)``,
  - ``json`` (access the response object directly, e.g.
    ``response['result']``), and
  - ``json_debug`` (`enable debugging
    <http://jsonrpcserver.readthedocs.org/api.html#response.ErrorResponse>`__
    and access the object directly, e.g. ``response['error']['data']``)

  Only the ``http_status`` attribute remains.

- ``dispatch()`` no longer takes a ``notification_errors`` parameter. To use
  that, instead set:: 

    from jsonrpcserver.response import ErrorResponse
    ErrorResponse.notification_errors = True

- Speed up processing by disabling request validation (if you're confident with
  the requests)::

    from jsonrpcserver.request import Request
    Request.schema_validation = True

3.1.1 (27 Oct 2015)
-------------------

- Notifications are no longer responded to, not even if there's an error. This
  is a `requirement <http://www.jsonrpc.org/specification#notification>`__ of
  the JSON-RPC specification. However, it can be overridden when calling
  `dispatch()
  <https://jsonrpcserver.readthedocs.org/api.html#dispatcher.dispatch>`__, to
  force notifications to receive errors.

- The HTTP status returned to notifications, which is 204 by default, can be
  `configured
  <https://jsonrpcserver.readthedocs.org/api.html#response.NotificationResponse.http_status>`__.

- Error responses can now be `configured
  <https://jsonrpcserver.readthedocs.org/api.html#exceptions>`__.

3.1.0 (17 Oct 2015)
-------------------

- `dispatch()
  <https://jsonrpcserver.readthedocs.org/api.html#dispatcher.dispatch>`__ now
  accepts a dictionary of name:method pairs, as an alternative to the usual list
  of methods.

3.0.0 (11 Oct 2015)
-------------------

Major update - much of the library has been rewritten. Although it works in much
the same way as before, upgraders are advised to read the new `documentation
<http://jsonrpcserver.readthedocs.org/>`__ to pick up the changes.
