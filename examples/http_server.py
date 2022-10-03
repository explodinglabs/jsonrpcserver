"""HTTPServer server

Demonstrates using Python's builtin http.server module to serve JSON-RPC.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

from jsonrpcserver import method, Result, Success, dispatch


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


class TestHttpServer(BaseHTTPRequestHandler):
    """HTTPServer request handler"""

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        """POST handler"""
        # Process request
        request = self.rfile.read(int(self.headers["Content-Length"])).decode()
        response = dispatch(request)
        # Return response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())


if __name__ == "__main__":
    HTTPServer(("localhost", 5000), TestHttpServer).serve_forever()
