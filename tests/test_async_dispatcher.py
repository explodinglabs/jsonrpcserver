"""Test async_dispatcher.py"""
from unittest.mock import Mock, patch
import pytest

from returns.result import Failure, Success

from jsonrpcserver.async_dispatcher import (
    call,
    dispatch_deserialized,
    dispatch_request,
    dispatch_to_response_pure,
)
from jsonrpcserver.main import default_deserializer, default_validator
from jsonrpcserver.codes import ERROR_INTERNAL_ERROR, ERROR_SERVER_ERROR
from jsonrpcserver.exceptions import JsonRpcError
from jsonrpcserver.request import Request
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from jsonrpcserver.result import ErrorResult, Ok, Result, SuccessResult
from jsonrpcserver.sentinels import NOCONTEXT, NODATA
from jsonrpcserver.utils import identity

# pylint: disable=missing-function-docstring,duplicate-code


async def ping() -> Result:
    return Ok("pong")


@pytest.mark.asyncio
async def test_call() -> None:
    assert await call(Request("ping", [], 1), NOCONTEXT, ping) == Success(
        SuccessResult("pong")
    )


@pytest.mark.asyncio
async def test_call_raising_jsonrpcerror() -> None:
    async def method_() -> Result:
        raise JsonRpcError(code=1, message="foo", data=NODATA)

    assert await call(Request("ping", [], 1), NOCONTEXT, method_) == Failure(
        ErrorResult(1, "foo")
    )


@pytest.mark.asyncio
async def test_call_raising_exception() -> None:
    async def method_() -> Result:
        raise ValueError("foo")

    assert await call(Request("ping", [], 1), NOCONTEXT, method_) == Failure(
        ErrorResult(ERROR_INTERNAL_ERROR, "Internal error", "foo")
    )


@pytest.mark.asyncio
async def test_dispatch_request() -> None:
    request = Request("ping", [], 1)
    assert await dispatch_request({"ping": ping}, NOCONTEXT, request) == (
        request,
        Success(SuccessResult("pong")),
    )


@pytest.mark.asyncio
async def test_dispatch_deserialized() -> None:
    assert await dispatch_deserialized(
        {"ping": ping},
        NOCONTEXT,
        identity,
        {"jsonrpc": "2.0", "method": "ping", "id": 1},
    ) == Success(SuccessResponse("pong", 1))


@pytest.mark.asyncio
async def test_dispatch_to_response_pure_success() -> None:
    assert await dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    ) == Success(SuccessResponse("pong", 1))


@patch("jsonrpcserver.async_dispatcher.dispatch_request", side_effect=ValueError("foo"))
@pytest.mark.asyncio
async def test_dispatch_to_response_pure_server_error(_: Mock) -> None:
    async def ping() -> Result:
        return Ok()

    assert await dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    ) == Failure(ErrorResponse(ERROR_SERVER_ERROR, "Server error", "ping", None))
