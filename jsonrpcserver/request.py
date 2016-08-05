"""A JSON-RPC request object. Used internally by the library, but class
attributes can be modified to configure various options for handling requests.
"""

import json
import logging
import re
import pkgutil
try:
    # Python 2
    from collections import Mapping, Sequence
except ImportError:
    # Python 3
    from collections.abc import Mapping, Sequence

from funcsigs import signature
import jsonschema

from jsonrpcserver import config
from jsonrpcserver.response import RequestResponse, NotificationResponse, \
    ExceptionResponse
from jsonrpcserver.exceptions import JsonRpcServerError, InvalidRequest, \
    InvalidParams, MethodNotFound

logger = logging.getLogger(__name__)

json_validator = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode('utf-8')))


def _get_method(methods, name):
    """Finds a method in a list (or dictionary).

    :param methods: List or dictionary of named functions.
    :param name: Name of the method to find.
    :raises MethodNotFound: If the method wasn't in the list.
    :returns: The method from the list.
    """
    # If it's a Mapping (dict-like), search for the key
    if isinstance(methods, Mapping):
        try:
            return methods[name]
        except KeyError:
            raise MethodNotFound(name)
    # Otherwise it must be a Sequence (list-like), search the __name__
    # attributes
    elif isinstance(methods, Sequence):
        try:
            return next(m for m in methods if m.__name__ == name)
        except StopIteration:
            raise MethodNotFound(name)


def _convert_camel_case(name):
    """Convert a camelCase string to under_score"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def _convert_camel_case_keys(original_dict):
    """Converts all keys of a dict from camelCase to under_score, recursively"""
    new_dict = dict()
    for k, v in original_dict.items():
        if isinstance(v, dict):
            # Recurse
            new_dict[_convert_camel_case(k)] = _convert_camel_case_keys(v)
        else:
            new_dict[_convert_camel_case(k)] = v
    return new_dict


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


def _validate_arguments_against_signature(func, args, kwargs):
    """Check if arguments match a function signature and can therefore be passed
    to it.

    :param func: The function object.
    :param args: List of positional arguments (or None).
    :param kwargs: Dict of keyword arguments (or None).
    :raises InvalidParams: If the arguments cannot be passed to the function.
    """
    try:
        if not args and not kwargs:
            signature(func).bind()
        elif args:
            signature(func).bind(*args)
        elif kwargs:
            signature(func).bind(**kwargs)
    except TypeError as e:
        raise InvalidParams(str(e))


def _call(methods, method_name, args=None, kwargs=None):
    """Find a method from a list, then validate the arguments before calling it.

    :param methods: The list of methods - either a python list, or Methods obj.
    :param args: Positional arguments (list)
    :param kwargs: Keyword arguments (dict)
    :raises MethodNotFound: If the method is not in the list.
    :raises InvalidParams: If the arguments don't match the method signature.
    :returns: The return value from the method called.
    """
    # Get the method object from a list of rpc methods
    method = _get_method(methods, method_name)
    # Ensure the arguments match the method's signature
    _validate_arguments_against_signature(method, args, kwargs)
    # Call the method
    if args and kwargs:
        # Cannot have both positional and keyword arguments in JSON-RPC.
        raise InvalidParams()
    # No arguments
    elif not args and not kwargs:
        return method()
    # Positional arguments
    elif args:
        return method(*args)
    # Keyword arguments
    elif kwargs:
        return method(**kwargs)


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

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a
    ``process`` method to execute the request.
    """

    def __init__(self, request):
        """
        :param request: JSON-RPC request, in dict or string form
        """
        # Validate against the JSON-RPC schema
        if config.schema_validation:
            _validate_against_schema(request)
        # Get method name from the request. We can assume the key exists because
        # the request passed the schema.
        self.method_name = request['method']
        # Get arguments from the request, if any
        self.args, self.kwargs = _get_arguments(request)
        # Get request id, if any
        self.request_id = request.get('id')
        # Convert camelCase to underscore
        if config.convert_camel_case:
            self.method_name = _convert_camel_case(self.method_name)
            if self.kwargs:
                self.kwargs = _convert_camel_case_keys(self.kwargs)

    @property
    def is_notification(self):
        """Returns True if the request is a JSON-RPC notification (ie. No
        response is required, False if it's a request.
        """
        return self.request_id is None

    def process(self, methods):
        """Calls the method and returns a Response object."""
        error = None
        try:
            result = _call(methods, self.method_name, self.args, self.kwargs)
        # Catch any JsonRpcServerError raised (Invalid Request, etc)
        except JsonRpcServerError as e:
            error = e
        # Catch uncaught exceptions and respond with ServerError
        except Exception as e: # pylint: disable=broad-except
            # Log the uncaught exception
            logger.exception(e)
            error = e # pylint: disable=redefined-variable-type
        if error:
            if self.is_notification and not config.notification_errors:
                return NotificationResponse()
            else:
                return ExceptionResponse(error, self.request_id)
        # Success
        if self.is_notification:
            return NotificationResponse()
        else:
            return RequestResponse(self.request_id, result)
