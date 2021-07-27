import pytest

from oslash.either import Right

from jsonrpcserver.async_dispatcher import (
    call,
    dispatch_deserialized,
    dispatch_request,
    dispatch_to_response_pure,
)
from jsonrpcserver.async_main import default_deserializer, default_schema_validator
from jsonrpcserver.request import Request
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Result, Success, SuccessResult
from jsonrpcserver.sentinels import NOCONTEXT
from jsonrpcserver.utils import identity


async def ping() -> Result:
    return Success("pong")


@pytest.mark.asyncio
async def test_call():
    assert await call(Request("ping", [], 1), NOCONTEXT, ping) == Right(
        SuccessResult("pong")
    )


@pytest.mark.asyncio
async def test_dispatch_request():
    request = Request("ping", [], 1)
    assert await dispatch_request({"ping": ping}, NOCONTEXT, request) == (
        request,
        Right(SuccessResult("pong")),
    )


@pytest.mark.asyncio
async def test_dispatch_deserialized():
    assert (
        await dispatch_deserialized(
            {"ping": ping},
            NOCONTEXT,
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
            context=NOCONTEXT,
            methods={"ping": ping},
            request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        )
        == Right(SuccessResponse("pong", 1))
    )
