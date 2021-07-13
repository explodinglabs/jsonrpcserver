from jsonrpcserver.request import Request


def test_request():
    assert Request(method="foo", params=[], id=1).method == "foo"


def test_request_invalid():
    # Should never happen, because the incoming request string is passed through the
    # jsonrpc schema before creating a Request
    pass
