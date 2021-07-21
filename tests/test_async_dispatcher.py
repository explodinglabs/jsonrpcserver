import pytest

from oslash.either import Right

from jsonrpcserver.async_dispatcher import (
    call,
    dispatch_deserialized,
    dispatch_request,
    dispatch_to_response_pure,
)
from jsonrpcserver.async_main import default_deserializer, default_schema_validator
from jsonrpcserver.dispatcher import DispatchResult
from jsonrpcserver.methods import Methods
from jsonrpcserver.request import Request
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Result, Success, SuccessResult
from jsonrpcserver.utils import identity


async def ping() -> Result:
    return Success("pong")


@pytest.mark.asyncio
async def test_call():
    assert await call(Request("ping", [], 1), None, ping) == Right(
        SuccessResult("pong")
    )


@pytest.mark.asyncio
async def test_dispatch_request():
    request = Request("ping", [], 1)
    assert await dispatch_request(Methods(ping), None, request) == DispatchResult(
        request, Right(SuccessResult("pong"))
    )


@pytest.mark.asyncio
async def test_dispatch_deserialized():
    assert (
        await dispatch_deserialized(
            Methods(ping),
            None,
            identity,
            {"jsonrpc": "2.0", "method": "ping", "id": 1},
        )
        == Right(SuccessResponse("pong", 1))
    )


@pytest.mark.asyncio
async def test_dispatch_to_response_pure_success():
    assert (
        await dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods=Methods(ping),
            request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        )
        == Right(SuccessResponse("pong", 1))
    )
