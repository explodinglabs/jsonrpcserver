"""rpc.py"""

from collections import OrderedDict

def result(request_id, data):
    """Success response.

    Note the "id" is required in the response, even if null, for both success
    and error. See http://www.jsonrpc.org/specification#response_object
    """

    return OrderedDict([
        ('jsonrpc', '2.0'),
        ('result', data),
        ('id', request_id)
    ])

def error(request_id, code, message, data=None):
    """Error response

    Note the "id" is required in the response, even if null, for both success
    and error. See http://www.jsonrpc.org/specification#response_object
    """

    e = OrderedDict([
        ('code', code),
        ('message', message)
    ])

    # Data is optional in the response.
    if data:
        e.update(OrderedDict([
            ('data', data)
        ]))

    return OrderedDict([
        ('jsonrpc', '2.0'),
        ('error', e),
        ('id', request_id)
    ])
