from unittest.mock import sentinel

from oslash.either import Left, Right

from jsonrpcserver.result import (
    Error,
    ErrorResult,
    InvalidParamsResult,
    NODATA,
    Success,
    SuccessResult,
)


def test_SuccessResult():
    assert SuccessResult(None).result is None


def test_SuccessResult_repr():
    assert repr(SuccessResult(None)) == "SuccessResult(None)"


def test_ErrorResult():
    result = ErrorResult(sentinel.code, sentinel.message)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == NODATA


def test_ErrorResult_repr():
    assert (
        repr(ErrorResult(1, "foo", None))
        == "ErrorResult(code=1, message='foo', data=None)"
    )


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


def test_Success():
    assert Success() == Right(SuccessResult(None))


def test_Error():
    assert Error(1, "foo", None) == Left(ErrorResult(1, "foo", None))
