"""request.py"""

import json
import pkgutil

import jsonschema
from six import string_types

from jsonrpcserver.exceptions import ParseError, InvalidRequest, InvalidParams


json_validator = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode('utf-8')))


def _string_to_dict(request):
    """Convert a JSON-RPC request string, to a dictionary.

    :param request: The JSON-RPC request string.
    :raises ValueError: If the string cannot be parsed to JSON.
    :returns: The same request in dict form.
    """
    try:
        return json.loads(request)
    except ValueError:
        raise ParseError()


def _validate_against_schema(request):
    """Validate against the JSON-RPC schema.

    :param request: JSON-RPC request dict.
    :raises InvalidRequest: If the request is invalid.
    :returns: None
    """
    try:
        json_validator.validate(request)
    except jsonschema.ValidationError as e:
        raise InvalidRequest(e.message)


def _get_arguments(request):
    """Takes the 'params' part of a JSON-RPC request and converts it to either
    positional or keyword arguments usable in Python. The value can be a JSON
    array (python list), object (python dict), or omitted. There are no other
    acceptable options. Note that a JSON-RPC request can have positional or
    keyword arguments, but not both! See
    http://www.jsonrpc.org/specification#parameter_structures

    :param request: JSON-RPC request in dict form.
    :raises InvalidParams: If 'params' was present but was not a list or dict.
    :returns: A tuple containing the positionals (in a list, or None) and
    keywords (in a dict, or None) extracted from the 'params' part of the
    request.
    """
    positionals = keywords = None
    params = request.get('params')
    # Params was omitted from the request. Taken as no arguments.
    if 'params' not in request:
        pass
    # Params is a list. Taken as positional arguments.
    elif isinstance(params, list):
        positionals = params
    # Params is a dict. Taken as keyword arguments.
    elif isinstance(params, dict):
        keywords = params
    # Anything else is invalid. (This should never happen if the request has
    # passed the schema validation.)
    else:
        raise InvalidParams('Params of type %s is not allowed' % \
            type(params).__name__)
    return (positionals, keywords)


class Request(object):
    """JSON-RPC Request object.

    Take a JSON-RPC request and provide details such as the method name,
    arguments, id, and whether it's a request or a notification.
    """

    def __init__(self, request, validate=True):
        """
        :param request: JSON-RPC request, in dict or string form
        :param validate: Check the request against the JSON-RPC schema?
        """
        # If the request is a string, convert it to a dict first
        if isinstance(request, string_types):
            request = _string_to_dict(request)
        # Validate against the JSON-RPC schema
        if validate:
            _validate_against_schema(request)
        # Get method name from the request. We can assume the key exists because
        # the request passed the schema.
        self.method_name = request['method']
        # Get arguments from the request, if any
        self.args, self.kwargs = _get_arguments(request)
        # Get request id, if any
        self.request_id = request.get('id')

    @property
    def is_notification(self):
        """Returns True if the request is a JSON-RPC notification (ie. No
        response is required, False if it's a request.
        """
        return self.request_id is None
