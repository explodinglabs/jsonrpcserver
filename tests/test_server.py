from unittest.mock import patch

from jsonrpcserver.server import serve


@patch("jsonrpcserver.server.HTTPServer")
def test_serve(*_):
    serve()
