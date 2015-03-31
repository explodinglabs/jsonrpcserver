"""status.py"""

# Taken from werkzeug/http.py
HTTP_STATUS_CODES = {
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',              # see RFC 3229
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',     # unused
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: 'I\'m a teapot',        # see RFC 2324
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',
    428: 'Precondition Required', # see RFC 6585
    429: 'Too Many Requests',
    431: 'Request Header Fields Too Large',
    449: 'Retry With',           # proprietary MS extension
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended'
}

# HTTP Status Codes

HTTP_200_OK = 200
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_500_INTERNAL_ERROR = 500

# JSONRPC status codes from http://www.jsonrpc.org/specification#error_object

JSONRPC_PARSE_ERROR_HTTP_CODE = HTTP_400_BAD_REQUEST
JSONRPC_PARSE_ERROR_CODE = -32700
JSONRPC_PARSE_ERROR_TEXT = 'Parse error'

JSONRPC_INVALID_REQUEST_HTTP_CODE = HTTP_400_BAD_REQUEST
JSONRPC_INVALID_REQUEST_CODE = -32600
JSONRPC_INVALID_REQUEST_TEXT = 'Invalid request'

JSONRPC_METHOD_NOT_FOUND_HTTP_CODE = HTTP_404_NOT_FOUND
JSONRPC_METHOD_NOT_FOUND_CODE = -32601
JSONRPC_METHOD_NOT_FOUND_TEXT = 'Method not found'

JSONRPC_INVALID_PARAMS_HTTP_CODE = HTTP_400_BAD_REQUEST
JSONRPC_INVALID_PARAMS_CODE = -32602
JSONRPC_INVALID_PARAMS_TEXT = 'Invalid params'

JSONRPC_SERVER_ERROR_HTTP_CODE = HTTP_500_INTERNAL_ERROR
JSONRPC_SERVER_ERROR_CODE = -32000
JSONRPC_SERVER_ERROR_TEXT = 'Server error'

def is_http_client_error(code):
    """Returns true if a status code is a 4xx Client Error.
    See http://en.wikipedia.org/wiki/List_of_HTTP_status_codes#4xx_Client_Error
    """
    return 400 <= code <= 499
