"""Test sentinels.py"""

from jsonrpcserver.sentinels import Sentinel


def test_sentinel() -> None:
    assert repr(Sentinel("foo")) == "<foo>"
