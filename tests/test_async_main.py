import pytest

from returns.result import Success

from jsonrpcserver.async_main import (
    dispatch_to_response,
    dispatch_to_serializable,
    dispatch_to_json,
)
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Result, Ok


async def ping() -> Result:
    return Ok("pong")


@pytest.mark.asyncio
async def test_dispatch_to_response():
    assert await dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == Success(SuccessResponse("pong", 1))


@pytest.mark.asyncio
async def test_dispatch_to_serializable():
    assert await dispatch_to_serializable(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == {"jsonrpc": "2.0", "result": "pong", "id": 1}


@pytest.mark.asyncio
async def test_dispatch_to_json():
    assert (
        await dispatch_to_json(
            '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
        )
        == '{"jsonrpc": "2.0", "result": "pong", "id": 1}'
    )


@pytest.mark.asyncio
async def test_dispatch_to_json_notification():
    assert (
        await dispatch_to_json('{"jsonrpc": "2.0", "method": "ping"}', {"ping": ping})
        == ""
    )
