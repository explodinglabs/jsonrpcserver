"""The methods passed to :func:`~dispatcher.dispatch` can be list of functions
like ``[eat, drink]``, a dictionary, or a ``Methods`` object::

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add
    def multiply(a, b):
        return a * b

    dispatch(methods, ...)
"""
import logging
try:
    # Python 2
    from collections import MutableMapping
except ImportError:
    # Python 3
    from collections.abc import MutableMapping
try:
    # Python 2
    from BaseHTTPServer import HTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer

from .log import log_
from .dispatcher import dispatch

_LOGGER = logging.getLogger(__name__)


class Methods(MutableMapping): #pylint:disable=too-many-ancestors
    """Holds a list of methods
    ... versionchanged:: 3.3
        Subclass MutableMapping instead of dict.
    """

    def __init__(self, *args, **kwargs):
        self._items = {}
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        # Method must be callable
        if not callable(value):
            raise TypeError('%s is not callable' % type(value))
        self._items[key] = value

    def __delitem__(self, key):
        del self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def add(self, method, name=None):
        """Add a method to the list::

            methods.add(multiply)

        Alternatively, use as a decorator::

            @methods.add
            def multiply(a, b):
                return a + b

        :param method: The method to add.
        :param name: Name of the method (optional).
        :raise AttributeError:
            Raised if the method being added has no name. (i.e. it has no
            ``__name__`` property, and no ``name`` argument was given.)
        """
        # If no custom name was given, use the method's __name__ attribute
        # Raises AttributeError otherwise
        if not name:
            name = method.__name__
        self.update({name: method})
        return method

    def add_method(self, *args, **kwargs):
        """
        ... deprecated:: 3.2.3
            Use add instead.
        """
        return self.add(*args, **kwargs)

    def serve_forever(self, name='', port=5000):
        """Serve the methods with a basic http server"""

        class RequestHandler(BaseHTTPRequestHandler):
            """Handles HTTP requests"""
            def do_POST(self): #pylint:disable=invalid-name
                """Takes a HTTP POST request, processes it and returns the result"""
                # Process request
                request = self.rfile.read(
                    int(self.headers['Content-Length'])).decode()
                response = dispatch(self.server.methods, request)
                # Return response
                self.send_response(response.http_status)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(str(response).encode())

        httpd = HTTPServer((name, port), RequestHandler)
        # Let the request handler know which methods to dispatch to
        httpd.methods = self
        log_(_LOGGER, 'info', ' * Listening on port %s', port)
        httpd.serve_forever()
