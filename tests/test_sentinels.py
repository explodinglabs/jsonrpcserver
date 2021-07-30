from jsonrpcserver.sentinels import Sentinel


def test_Sentinel():
    assert repr(Sentinel("foo")) == "<foo>"
