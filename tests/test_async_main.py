"""Test async_main.py"""

import pytest
from returns.result import Success

from jsonrpcserver.async_main import (
    dispatch_to_json,
    dispatch_to_response,
    dispatch_to_serializable,
)
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Ok, Result

# pylint: disable=missing-function-docstring

# pylint: disable=missing-function-docstring


async def ping() -> Result:
    return Ok("pong")


@pytest.mark.asyncio
async def test_dispatch_to_response() -> None:
    assert await dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == Success(SuccessResponse("pong", 1))


@pytest.mark.asyncio
async def test_dispatch_to_serializable() -> None:
    assert await dispatch_to_serializable(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == {"jsonrpc": "2.0", "result": "pong", "id": 1}


@pytest.mark.asyncio
async def test_dispatch_to_json() -> None:
    assert (
        await dispatch_to_json(
            '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
        )
        == '{"jsonrpc": "2.0", "result": "pong", "id": 1}'
    )


@pytest.mark.asyncio
async def test_dispatch_to_json_notification() -> None:
    assert (
        await dispatch_to_json('{"jsonrpc": "2.0", "method": "ping"}', {"ping": ping})
        == ""
    )
