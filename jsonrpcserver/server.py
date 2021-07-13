import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from .main import dispatch


def serve(name: str = "", port: int = 5000) -> None:
    class RequestHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            response = dispatch(
                self.rfile.read(int(str(self.headers["Content-Length"]))).decode()
            )
            if response is not None:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(str(response).encode())

    logging.info(" * Listening on port %s", port)
    HTTPServer((name, port), RequestHandler).serve_forever()
