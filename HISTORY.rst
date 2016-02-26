Recent Changes
==============

3.2.2 (26 Feb 2016)
-------------------

- I was frustrated handling requests with camelCase key names. (which they
  should be in JSON right?). So now simply set
  ``Request.convert_camel_case_keys = True`` and continue as though they were
  underscores. See example below::

    from jsonrpcserver import dispatch
    from jsonrpcserver.request import Request
    Request.convert_camel_case_keys = True

    # Can be handled with underscores like this::
    def get_customer(**kwargs):
        return 'Found {}'.format(kwargs['first_name'])

    # A request with camelcase method and params like this::
    req = {"jsonrpc": "2.0", "method": "getCustomer", "params: {"firstName": "Beau"}, "id": 1}
    dispatch([get_customer], req)
