"""
Request module.

The Request class represents a JSON-RPC request object. Used internally by the
library, but class attributes can be modified to configure various options for
handling requests.
"""
from contextlib import contextmanager
import logging
import traceback

from . import config
from .exceptions import JsonRpcServerError
from .log import log_
from .request_utils import * # Bad
from .response import (
    Response, RequestResponse, NotificationResponse, ExceptionResponse)


_LOGGER = logging.getLogger(__name__)


class Request(object):
    """
    Represents a JSON-RPC Request object.

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a
    ``process`` method to execute the request.
    """
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
        except Exception as exc:
            # Log the exception if it wasn't explicitly raised by the method
            if not isinstance(exc, JsonRpcServerError):
                log_(_LOGGER, 'error', traceback.format_exc())
            # Notifications should not be responded to, even for errors (unless
            # overridden in configuration)
            if self.is_notification and not config.notification_errors:
                self.response = NotificationResponse()
            else:
                self.response = ExceptionResponse(
                    exc, getattr(self, 'request_id', None))

    def __init__(self, request, context=None):
        """
        :param request: JSON-RPC request, in dict form
        """
        # Handle parsing & validation errors
        with self.handle_exceptions():
            # Validate against the JSON-RPC schema
            if config.schema_validation:
                validate_against_schema(request)
            # Get method name from the request. We can assume the key exists
            # because the request passed the schema.
            self.method_name = request['method']
            # Get arguments from the request, if any
            self.args, self.kwargs = get_arguments(request.get('params'), context=context)
            # Get request id, if any
            self.request_id = request.get('id')
            # Convert camelCase to underscore
            if config.convert_camel_case:
                self.method_name = convert_camel_case(self.method_name)
                if self.kwargs:
                    self.kwargs = convert_camel_case_keys(self.kwargs)
            self.response = None

    def call(self, methods):
        """
        Call the appropriate method from a list.

        Find the method from the passed list, and call it, returning a Response
        """
        # Validation or parsing may have failed in __init__, in which case
        # there's no point calling. It would've already set the response.
        if not self.response:
            # Handle setting the result/exception of the call
            with self.handle_exceptions():
                # Get the method object from a list (raises MethodNotFound)
                callable_ = self._get_method(methods)
                # Ensure the arguments match the method's signature
                validate_arguments_against_signature(callable_, self.args, self.kwargs)
                # Call the method
                result = callable_(*(self.args or []), **(self.kwargs or {}))
                # Set the response
                if self.is_notification:
                    self.response = NotificationResponse()
                else:
                    self.response = RequestResponse(self.request_id, result)
        # Ensure the response has been set before returning it
        assert isinstance(self.response, Response), 'Invalid response type'
        return self.response

    def _get_method(self, methods):
        """
        Find and return a callable representing the method for this request.

        :param methods: List or dictionary of named functions
        :raises MethodNotFound: If no method is found
        :returns: Callable representing the method
        """
        return get_method(methods, self.method_name)
