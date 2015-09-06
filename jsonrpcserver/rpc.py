"""rpc.py"""

from collections import OrderedDict

def sort_response(response):
    """Sorts a JSON-RPC response dict returning a sorted OrderedDict, having no
    effect other than making it nicer to read.

    >>> json.dumps(sort_response(
    ...     {'id': 2, 'result': 5, 'jsonrpc': '2.0'}))
    '{"jsonrpc": "2.0", "method": "add", "result": 5, "id": 1}'

    :param response: JSON-RPC response in dict format.
    :return: The same response, nicely sorted.
    """
    if response:
        sort_order = ['jsonrpc', 'result', 'error', 'id']
        return OrderedDict(sorted(response.items(), key=lambda k: \
            sort_order.index(k[0])))


def rpc_success_response(request_id, data):
    """Success response.

    Note the 'id' is required in the response, even if null, for both success
    and error. See http://www.jsonrpc.org/specification#response_object

    :param request_id: The id of the request, or None.
    :param data: The result - could be a string, number, dict or list.
    :return: The response dict.
    """
    return {
        'jsonrpc': '2.0',
        'result': data,
        'id': request_id
    }


def rpc_error_response(request_id, code, message, data=None):
    """Error response

    Note the 'id' is required in the response, even if null, for both success
    and error. See http://www.jsonrpc.org/specification#response_object

    :param request_id: The id of the request, or None.
    :param code: The JSON-RPC error code. See
        http://www.jsonrpc.org/specification#error_object
    :param message: The error message.
    :param data: Extra information about the error (optional). Could be a
        string, number, dict or list.
    :return: The response dict.
    """
    response = {
        'jsonrpc': '2.0',
        'error': {
            'code': code,
            'message': message
        },
        'id': request_id
    }
    # Data is optional in the response.
    if data:
        response['error']['data'] = data
    return response
