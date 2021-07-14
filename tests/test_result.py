from unittest.mock import sentinel

from jsonrpcserver.result import (
    SuccessResult,
    ErrorResult,
    InvalidParamsResult,
    NODATA,
)


def test_SuccessResult():
    assert SuccessResult(None).result is None


def test_ErrorResult():
    result = ErrorResult(sentinel.code, sentinel.message)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == NODATA


def test_ErrorResult_with_data():
    result = ErrorResult(sentinel.code, sentinel.message, sentinel.data)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == sentinel.data


def test_InvalidParamsResult():
    result = InvalidParamsResult(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data


def test_InvalidParamsResult_with_data():
    result = InvalidParamsResult(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data
