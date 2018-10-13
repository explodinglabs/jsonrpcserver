import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from .dispatcher import dispatch


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        """HTTP POST"""
        # Process request
        request = self.rfile.read(int(str(self.headers["Content-Length"]))).decode()
        response = dispatch(request)
        # Return response
        if response.wanted:
            self.send_response(response.http_status)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(str(response).encode())


def serve(name: str = "", port: int = 5000) -> None:
    """
    A basic way to serve the methods.

    Args:
        name: Server address.
        port: Server port.
    """
    logging.info(" * Listening on port %s", port)
    httpd = HTTPServer((name, port), RequestHandler)
    httpd.serve_forever()
