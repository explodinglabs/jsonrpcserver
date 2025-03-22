"""A simple development server for serving JSON-RPC requests using Python's builtin
http.server module.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer

from .main import dispatch


class RequestHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests"""

    def do_POST(self) -> None:
        """Handle POST request"""
        request = self.rfile.read(int(str(self.headers["Content-Length"]))).decode()
        response = dispatch(request)
        if response is not None:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())


def serve(name: str = "", port: int = 5000) -> None:
    httpd = HTTPServer((name, port), RequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.shutdown()
