from jsonrpcserver import status


def test_is_http_client_error():
    assert status.is_http_client_error(status.HTTP_BAD_REQUEST) is True
    assert status.is_http_client_error(status.HTTP_INTERNAL_ERROR) is False
