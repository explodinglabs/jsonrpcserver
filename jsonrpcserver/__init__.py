import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from .methods import add as method, global_methods
from .dispatcher import dispatch


def serve(name="", port=5000):
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
            response = dispatch(request)
            # Return response
            if response.wanted:
                self.send_response(response.http_status)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(response).encode())

    httpd = HTTPServer((name, port), RequestHandler)
    # Let the request handler know which methods to dispatch to
    httpd.methods = global_methods
    logging.info(" * Listening on port %s", port)
    httpd.serve_forever()
