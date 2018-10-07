from .methods import add as method
from .dispatcher import dispatch
from .async_dispatcher import dispatch as async_dispatch


def serve(name: str = "", port: int =5000) -> None:
    """
    A basic way to serve the methods.

    Args:
        name: Server address.
        port: Server port.
    """
    import logging
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from .methods import global_methods

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

    httpd = HTTPServer((name, port), RequestHandler)
    logging.info(" * Listening on port %s", port)
    httpd.serve_forever()
