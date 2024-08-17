"""Test result.py"""

from unittest.mock import sentinel

from returns.result import Failure, Success

from jsonrpcserver.result import (
    Error,
    ErrorResult,
    InvalidParamsResult,
    Ok,
    SuccessResult,
)
from jsonrpcserver.sentinels import NODATA


def test_SuccessResult() -> None:
    assert SuccessResult(None).result is None


def test_SuccessResult_repr() -> None:
    assert repr(SuccessResult(None)) == "SuccessResult(None)"


def test_ErrorResult() -> None:
    result = ErrorResult(sentinel.code, sentinel.message)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == NODATA


def test_ErrorResult_repr() -> None:
    assert (
        repr(ErrorResult(1, "foo", None))
        == "ErrorResult(code=1, message='foo', data=None)"
    )


def test_ErrorResult_with_data() -> None:
    result = ErrorResult(sentinel.code, sentinel.message, sentinel.data)
    assert result.code == sentinel.code
    assert result.message == sentinel.message
    assert result.data == sentinel.data


def test_InvalidParamsResult() -> None:
    result = InvalidParamsResult(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data


def test_InvalidParamsResult_with_data() -> None:
    result = InvalidParamsResult(sentinel.data)
    assert result.code == -32602
    assert result.message == "Invalid params"
    assert result.data == sentinel.data


def test_Ok() -> None:
    assert Ok() == Success(SuccessResult(None))


def test_Error() -> None:
    assert Error(1, "foo", None) == Failure(ErrorResult(1, "foo", None))
