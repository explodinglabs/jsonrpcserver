"""At the core of jsonrpcserver is the dispatcher, which processes JSON-RPC
requests.

::

    from jsonrpcserver import dispatch
"""
import logging
import json

from six import string_types

from .log import log_
from .response import NotificationResponse, ExceptionResponse, BatchResponse
from .request import Request
from .exceptions import JsonRpcServerError, ParseError, InvalidRequest
from .status import HTTP_STATUS_CODES
from . import config

_REQUEST_LOG = logging.getLogger(__name__+'.request')
_RESPONSE_LOG = logging.getLogger(__name__+'.response')


class Requests(object): #pylint:disable=too-few-public-methods
    """Requests"""

    @staticmethod
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

    @staticmethod
    def _log_response(response):
        """Log a response"""
        log_(_RESPONSE_LOG, 'info', str(response), fmt='<-- %(message)s',
             extra={'http_code': response.http_status,
                    'http_reason': HTTP_STATUS_CODES[response.http_status]})

    def __init__(self, requests, request_type=Request):
        """Logs the request, and builds a list of Requests. Will set the
        respnose attribute if there's an problem with the request."""
        self.requests = requests
        self.response = None
        self.request_type = request_type
        # Log the request
        if config.log_requests:
            log_(_REQUEST_LOG, 'info', requests, fmt='--> %(message)s')
        try:
            # If the request is a string, convert it to a dict
            if isinstance(requests, string_types):
                self.requests = self._string_to_dict(self.requests)
            # Empty batch requests are invalid
            # http://www.jsonrpc.org/specification#examples
            if isinstance(requests, list) and not requests:
                raise InvalidRequest()
        # Set the response attribute if there's a problem with the request
        except JsonRpcServerError as exc:
            self.response = ExceptionResponse(exc, None)

    def dispatch(self, methods):
        """Process a JSON-RPC request, calling the requested method(s).

        .. code-block:: python

            >>> request = {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
            >>> response = dispatch({'ping': lambda: 'pong'}, request)
            --> {'jsonrpc': '2.0', 'method': 'ping', 'id': 1}
            <-- {'jsonrpc': '2.0', 'result': 'pong', 'id': 1}

        :param methods:
            Collection of methods to dispatch to. Can be a ``list`` of
            functions, a ``dict`` of name:method pairs, or a ``Methods`` object.
        :param request:
            A JSON-RPC request. Can be a JSON-serializable object, or a string.
            (Strings must be valid JSON - use double quotes!)
        :returns:
            A :mod:`response` object.
        """
        # Init may have failed to parse the request, in which case the response
        # would already be set
        if not self.response:
            # Batch request
            if isinstance(self.requests, list):
                # Batch requests - call each request, and exclude Notifications
                # from the list of responses
                self.response = BatchResponse(
                    [r.call(methods) for r in map(self.request_type,
                     self.requests) if not r.is_notification])
                # If the response list is empty, return nothing
                if not self.response:
                    self.response = NotificationResponse() #pylint:disable=redefined-variable-type
            # Single request
            else:
                self.response = self.request_type(self.requests).call(methods)
        assert self.response, 'Response must be set'
        assert self.response.http_status, 'Must have http_status set'
        if config.log_responses:
            self._log_response(self.response)
        return self.response


def dispatch(methods, requests):
    """Main public dispatch method"""
    return Requests(requests).dispatch(methods)
