Release History
===============

2.1.0 (2015-09-06)
------------------

- Debug mode can now be enabled by setting a flag on the dispatcher. This allows
  extra (potentially sensitive) information to be included in the response
  message to the client. *The previous method (passing ``more_info=True`` to the
  dispatch method) has been removed.*

2.0.2 (2015-09-04)
------------------

- Faster request validation.
  (`#23 <https://bitbucket.org/beau-barker/jsonrpcserver/issues/23/performance-of-jsonrpcserver-is-not-very>`_)

2.0.1 (2015-05-09)
------------------

- Fixed logging, now allows you to add handlers to getLogger('jsonrpcserver').
  See docs for info.
