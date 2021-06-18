from unittest.mock import sentinel

from jsonrpcserver.result import Success, Error, InvalidParams, UNSPECIFIED


def test_Success():
    assert Success(None).result is None


def test_Error():
    result = Error(sentinel.code, sentinel.message)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == UNSPECIFIED


def test_Error_with_data():
    result = Error(sentinel.code, sentinel.message, sentinel.data)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == sentinel.data


def test_InvalidParams():
    result = InvalidParams(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data


def test_InvalidParams_with_data():
    result = InvalidParams(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data
