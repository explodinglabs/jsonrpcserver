"""
The "methods" object holds the list of functions that can be called by RPC calls.

Use the `add` decorator to register a method to the list::

    from jsonrpcserver import methods

    @methods.add
    def ping():
        return 'pong'

Add as many methods as needed.

Methods can take either positional or named arguments (but not both, this is a
limitation of JSON-RPC).

Serve the methods::

    >>> methods.serve_forever()
     * Listening on port 5000
"""
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable


logger = logging.getLogger(__name__)


class Methods:
    """Holds a list of methods that can be called with a JSON-RPC request."""

    def __init__(self):
        self.items = {}

    def add(self, method, name=None):
        """
        Register a function to the list.

        Args:
            method: Function to register to the list.
            name: Optionally give a name (or rename) the original function.

        Returns:
            None

        Raises:
            AttributeError: Raised if the method being added has no name. (i.e. it has
                no ``__name__`` property, and no ``name`` argument was given.)

        Examples:
            @methods.add
            def subtract(minuend, subtrahend):
                return minuend - subtrahend
        """
        assert callable(method)
        # If no custom name was given, use the method's __name__ attribute
        # Raises AttributeError otherwise
        name = method.__name__ if not name else name
        self.items[name] = method
        return method  # for the decorator to work

    def get(self, name: str) -> Callable:
        """
        Get a method in the list.

        Args:
            name: Name of the method to find.

        Returns:
            The method from the list.

        Raises:
            KeyError: If the method wasn't in the list.
        """
        return self.items[name]

    def serve_forever(self, name="", port=5000):
        """
        A basic way to serve the methods.

        Args:
            name: Server address.
            port: Server port.
        """

        class RequestHandler(BaseHTTPRequestHandler):
            """Request handler"""

            def do_POST(self):
                """HTTP POST"""
                # Process request
                request = self.rfile.read(int(self.headers["Content-Length"])).decode()
                response = dispatch(self.server.methods, request)
                # Return response
                self.send_response(response.http_status)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(response).encode())

        httpd = HTTPServer((name, port), RequestHandler)
        # Let the request handler know which methods to dispatch to
        httpd.methods = self
        logging.info(" * Listening on port %s", port)
        httpd.serve_forever()
