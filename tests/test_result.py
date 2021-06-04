from unittest.mock import sentinel

from jsonrpcserver.result import Success, Error, InvalidParams, UNSPECIFIED


def test_Success():
    assert Success(None).result is None


def test_Error():
    result = Error(-1, "foo")
    assert result.code == -1
    assert result.message == "foo"
    assert result.data == UNSPECIFIED


def test_Error_with_data():
    result = Error(-1, "foo", sentinel.data)
    assert result.code == -1
    assert result.message == "foo"
    assert result.data == sentinel.data


def test_InvalidParams():
    result = InvalidParams("foo")
    assert result.code == -32602
    assert result.message == "foo"
    assert result.data == UNSPECIFIED


def test_InvalidParams_with_data():
    result = InvalidParams("foo", sentinel.data)
    assert result.code == -32602
    assert result.message == "foo"
    assert result.data == sentinel.data
