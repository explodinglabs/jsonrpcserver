Release History
===============

2.1.2 (2015-09-06)
------------------

- Debugging mode can now be enabled by setting the debug flag on the dispatcher.
  (for example, ``dispatcher = Dispatcher(debug=True)`` or ``dispatcher.debug =
  True``). Debug mode allows extra (potentially sensitive) information to be
  included in the response message to the client. Default is False. *Previously
  debugging was done by passing ``more_info=True`` in the dispatch method - that
  method no longer works.*

2.0.2 (2015-09-04)
------------------

- Faster request validation.
  (`#23 <https://bitbucket.org/beau-barker/jsonrpcserver/issues/23/performance-of-jsonrpcserver-is-not-very>`_)

2.0.1 (2015-05-09)
------------------

- Fixed logging, now allows you to add handlers to getLogger('jsonrpcserver').
  See docs for info.
