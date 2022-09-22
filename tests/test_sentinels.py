from jsonrpcserver.sentinels import Sentinel


def test_Sentinel() -> None:
    assert repr(Sentinel("foo")) == "<foo>"
