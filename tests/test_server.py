"""Test server.py"""

from unittest.mock import Mock, patch

from jsonrpcserver.server import serve


@patch("jsonrpcserver.server.HTTPServer")
def test_serve(*_: Mock) -> None:
    serve()
