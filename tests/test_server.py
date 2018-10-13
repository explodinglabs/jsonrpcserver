from unittest.mock import patch

from jsonrpcserver.server import RequestHandler, serve


@patch("jsonrpcserver.server.HTTPServer")
def test_serve(*_):
    serve()
