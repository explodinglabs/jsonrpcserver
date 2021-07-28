import pytest

from oslash.either import Right

from jsonrpcserver.async_main import (
    dispatch_to_response,
    dispatch_to_serializable,
    dispatch_to_json,
)
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Result, Success


async def ping() -> Result:
    return Success("pong")


@pytest.mark.asyncio
async def test_dispatch_to_response():
    assert await dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == Right(SuccessResponse("pong", 1))


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
