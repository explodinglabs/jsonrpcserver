"""rpc.py"""

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
    e = {
        'code': code,
        'message': message
    }
    # Data is optional in the response.
    if data:
        e.update({
            'data': data
        })
    return {
        'jsonrpc': '2.0',
        'error': e,
        'id': request_id
    }
