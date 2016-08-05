"""A basic HTTP server which takes JSON-RPC request via HTTP POST, processes it
and returns a JSON-RPC response object.

https://docs.python.org/3/library/http.server.html
"""
import logging
try:
    # Python 2
    import SimpleHTTPServer as HTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    # Python 3
    from http.server import BaseHTTPRequestHandler, HTTPServer

from jsonrpcserver.log import _log
from jsonrpcserver.dispatcher import dispatch

logger = logging.getLogger(__name__)


class RequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP requests"""

    def do_POST(self):
        """Takes a HTTP POST request, processes it and returns the result"""
        # Process request
        request = self.rfile.read(
            int(self.headers['Content-Length'])).decode('utf-8')
        r = dispatch(self.server.methods, request)
        # Return response
        self.send_response(r.http_status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(str(r).encode('utf-8'))


class MethodsServer(object):
    """HTTP server mixin"""

    def serve_forever(self, name='', port=5000):
        """Start the server"""
        httpd = HTTPServer((name, port), RequestHandler)
        # Let the request handler know which methods to dispatch to
        httpd.methods = self
        _log(logger, 'info', ' * Listening on port %s', port)
        httpd.serve_forever()
