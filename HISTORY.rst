Recent Changes
==============

3.2.2 (26 Feb 2016)
-------------------

- Added ``Request.convert_camel_case`` option.

A common problem was handling requests with *camelCase* methods and key names,
like this::

    {
        'jsonrpc': '2.0',
        'method': 'getCustomer',
        'params: {
            'firstName': 'Beau'
        },
        'id': 1
    }

These requests were awkward to handle because of the camel-case names. One had
to convert ``firstName`` to ``first_name``, or use camel-case inside the python
functions, which is just ugly.

An option was added to automatically convert them to underscore format, making
handling these requests much simpler::

    from jsonrpcserver import dispatch
    from jsonrpcserver.request import Request
    Request.convert_camel_case = True

    def get_customer(**kwargs):
        return 'Found {}'.format(kwargs['first_name'])

    >>> dispatch([get_customer], {'jsonrpc': '2.0', 'method': 'getCustomer', 'params: {'firstName': 'Beau'}, 'id': 1})
    {'jsonrpc': '2.0', 'result': 'Found Beau', 'id': 1}

Easy!
