Release History
---------------

1.0.12 (2015-03-04)
^^^^^^^^^^^^^^^^^^^

- Minor bug fixes.

1.0.11 (2015-02-12)
^^^^^^^^^^^^^^^^^^^

- Ability to log the http headers. See `Logging
  <https://jsonrpcserver.readthedocs.org/#logging>`_.


1.0.10 (2014-12-31)
^^^^^^^^^^^^^^^^^^^

- Important! The `dispatch` method now requires two arguments. Change
  `dispatch(HandleRequests)` to `dispatch(request.get_json(),
  HandleRequests)`. This gives you the freedom to customize the way flask
  retrieves the json request. For example, pass `force=True` to ignore the
  mimetype sent from the client. See `get_json
  <http://flask.pocoo.org/docs/0.10/api/#flask.Request.get_json>`_.

- Blueprint error handling improved. Now gives certain errors, such as Internal
  Server Error, in the format requested by the client (in the Accept header).


1.0.9 (2014-12-31)
^^^^^^^^^^^^^^^^^^

- Bugfix: Fixed a critical bug where the blueprint wasn't catching exceptions!
- Logging has changed. See `Logging
  <https://jsonrpcserver.readthedocs.org/#logging>`_.

1.0.8 (2014-12-30)
^^^^^^^^^^^^^^^^^^

- Bugfix: an important schema file wasn't being included in the distribution.

1.0.7 (2014-12-30)
^^^^^^^^^^^^^^^^^^

- The dispatch module renamed to *dispatcher*, to avoid conflicting with the
  dispatch method.

1.0.6 (2014-12-11)
^^^^^^^^^^^^^^^^^^

- Improved blueprint, with correct http status code responses.
- Gives more information when rejecting a request.
- Major rebuild of the exceptions.
- More stability with 100% code coverage in tests.

1.0.5 (2014-12-02)
^^^^^^^^^^^^^^^^^^

- Messages are now output on the INFO log level.
- Show the status code in response log entries.
