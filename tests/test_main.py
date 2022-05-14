from returns.result import Success

from jsonrpcserver.main import (
    dispatch_to_response,
    dispatch_to_serializable,
    dispatch_to_json,
)
from jsonrpcserver.response import SuccessResponse
from jsonrpcserver.result import Result, Ok


def ping() -> Result:
    return Ok("pong")


def test_dispatch_to_response():
    assert dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == Success(SuccessResponse("pong", 1))


def test_dispatch_to_serializable():
    assert dispatch_to_serializable(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    ) == {"jsonrpc": "2.0", "result": "pong", "id": 1}


def test_dispatch_to_json():
    assert (
        dispatch_to_json(
            '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
        )
        == '{"jsonrpc": "2.0", "result": "pong", "id": 1}'
    )


def test_dispatch_to_json_notification():
    assert (
        dispatch_to_json('{"jsonrpc": "2.0", "method": "ping"}', {"ping": ping}) == ""
    )
