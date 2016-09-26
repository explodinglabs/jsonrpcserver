"""A JSON-RPC request object. Used internally by the library, but class
attributes can be modified to configure various options for handling requests.
"""

import json
import logging
import traceback
import re
import pkgutil
try:
    # Python 2
    from collections import Mapping, Sequence
except ImportError:
    # Python 3
    from collections.abc import Mapping, Sequence
from contextlib import contextmanager

from funcsigs import signature
import jsonschema

from . import config
from .log import log_
from .response import RequestResponse, NotificationResponse, ExceptionResponse
from .exceptions import JsonRpcServerError, InvalidRequest, InvalidParams, \
    MethodNotFound

_LOGGER = logging.getLogger(__name__)

_JSON_VALIDATOR = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode()))


def _convert_camel_case(name):
    """Convert a camelCase string to under_score"""
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def _convert_camel_case_keys(original_dict):
    """Converts all keys of a dict from camelCase to under_score, recursively"""
    new_dict = dict()
    for key, val in original_dict.items():
        if isinstance(val, dict):
            # Recurse
            new_dict[_convert_camel_case(key)] = _convert_camel_case_keys(val)
        else:
            new_dict[_convert_camel_case(key)] = val
    return new_dict


class Request(object):
    """JSON-RPC Request object.

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a
    ``process`` method to execute the request.
    """

    @staticmethod
    def _validate_against_schema(request):
        """Validate against the JSON-RPC schema.

        :param request: JSON-RPC request dict.
        :raises InvalidRequest: If the request is invalid.
        :returns: None
        """
        try:
            _JSON_VALIDATOR.validate(request)
        except jsonschema.ValidationError as exc:
            raise InvalidRequest(exc.message)

    def _validate_arguments_against_signature(self, func):
        """Check if arguments match a function signature and can therefore be
        passed to it.

        :param func: The function object.
        :param args: List of positional arguments (or None).
        :param kwargs: Dict of keyword arguments (or None).
        :raises InvalidParams: If the arguments cannot be passed to the
        function.
        """
        try:
            signature(func).bind(*(self.args or []), **(self.kwargs or {}))
        except TypeError as exc:
            raise InvalidParams(str(exc))

    @staticmethod
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
        # Otherwise it must be a Sequence, search the __name__ attributes of
        # its items
        elif isinstance(methods, Sequence):
            try:
                return next(m for m in methods if m.__name__ == name)
            except StopIteration:
                raise MethodNotFound(name)

    @staticmethod
    def _get_arguments(request):
        """Takes the 'params' part of a JSON-RPC request and converts it to
        either positional or keyword arguments usable in Python. The value can
        be a JSON array (python list), object (python dict), or omitted. There
        are no other acceptable options. Note that a JSON-RPC request can have
        positional or keyword arguments, but not both! See
        http://www.jsonrpc.org/specification#parameter_structures

        :param request: JSON-RPC request in dict form.
        :raises InvalidParams: If 'params' was present but was not a list or
            dict.
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
        # Any other type is invalid. (This should never happen if the request
        # has passed the schema validation.)
        else:
            raise InvalidParams('Params of type %s is not allowed' % \
                type(params).__name__)
        assert not (positionals and keywords), \
            'Cannot have both positional and keyword arguments in JSON-RPC.'
        return (positionals, keywords)

    @property
    def is_notification(self):
        """Returns True if the request is a JSON-RPC Notification (ie. No id
        attribute is included). False if it's a request.
        """
        return hasattr(self, 'request_id') and self.request_id is None

    @contextmanager
    def handle_exceptions(self):
        """Sets the response value"""
        try:
            yield
        except Exception as exc: #pylint:disable=broad-except
            # Log the exception if it wasn't explicitly raised by the method
            if not isinstance(exc, JsonRpcServerError):
                log_(_LOGGER, 'error', traceback.format_exc())
            # Notifications should not be responded to, even for errors (unless
            # overridden in configuration)
            if self.is_notification and not config.notification_errors:
                self.response = NotificationResponse()
            else:
                self.response = ExceptionResponse( #pylint:disable=redefined-variable-type
                    exc, getattr(self, 'request_id', None))

    def __init__(self, request):
        """
        :param request: JSON-RPC request, in dict form
        """
        # Handle validation/parse exceptions
        with self.handle_exceptions():
            # Validate against the JSON-RPC schema
            if config.schema_validation:
                self._validate_against_schema(request)
            # Get method name from the request. We can assume the key exists
            # because the request passed the schema.
            self.method_name = request['method']
            # Get arguments from the request, if any
            self.args, self.kwargs = self._get_arguments(request)
            # Get request id, if any
            self.request_id = request.get('id')
            # Convert camelCase to underscore
            if config.convert_camel_case:
                self.method_name = _convert_camel_case(self.method_name)
                self.kwargs = _convert_camel_case_keys(self.kwargs)
            self.response = None

    def call(self, methods):
        """Find the method from the passed list, and call it, returning a
        Response"""
        # Validation or parsing may have failed in __init__, in which case
        # there's no point calling. It would've already set the response.
        if not self.response:
            # call_context handles setting the result/exception of the call
            with self.handle_exceptions():
                # Get the method object from a list (raises MethodNotFound)
                callable_ = self._get_method(methods, self.method_name)
                # Ensure the arguments match the method's signature
                self._validate_arguments_against_signature(callable_)
                # Call the method
                result = callable_(*(self.args or []), **(self.kwargs or {}))
                # Set the response
                if self.is_notification:
                    self.response = NotificationResponse()
                else:
                    self.response = RequestResponse(self.request_id, result) #pylint:disable=redefined-variable-type
        # Ensure the response has been set
        assert self.response, 'Call must set response'
        assert isinstance(self.response, (ExceptionResponse, \
            NotificationResponse, RequestResponse)), 'Invalid response type'
        return self.response
