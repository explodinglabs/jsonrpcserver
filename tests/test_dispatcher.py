"""TODO: Add tests for dispatch_requests (non-pure version)"""
import json
from typing import Any
from unittest.mock import sentinel

from jsonrpcserver import status
from jsonrpcserver.dispatcher import (
    create_requests,
    dispatch_request,
    dispatch_to_response,
    dispatch_to_response_pure,
)
from jsonrpcserver.methods import Methods, global_methods
from jsonrpcserver.result import Result, Success
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import ErrorResponse, SuccessResponse


# def test_dispatch_to_response_pure_invalid_params_notification():
#    def foo(bar):
#        if bar < 0:
#            raise InvalidRequestError("bar must be greater than zero")
#    response = dispatch_to_response_pure(str(Notify("foo")), method


def ping() -> Result:
    return Success("pong")


# dispatch_request


def test_dispatch_request_success_result():
    response = dispatch_request(
        methods=Methods(ping), context=None, request=Request("ping", [], 1)
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"


def test_dispatch_request_notification():
    response = dispatch_request(
        methods=Methods(ping), context=None, request=Request("ping", [], NOID)
    )
    assert response is None


def test_dispatch_request_notification_failure():
    """
    Should not respond. From the spec: Notifications are not confirmable by
    definition, since they do not have a Response object to be returned. As
    such, the Client would not be aware of any errors (like e.g. "Invalid
    params","Internal error").
    """

    def fail(request: Request):
        1 / 0

    response = dispatch_request(
        methods=Methods(fail), context=None, request=Request("fail", [], NOID)
    )
    assert response is None


def test_dispatch_request_method_not_found():
    response = dispatch_request(
        methods=Methods(ping), context=None, request=Request("nonexistant", [], 1)
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == -32601
    assert response.message == "Method not found"
    assert response.id == 1


def test_dispatch_request_invalid_params():
    response = dispatch_request(
        methods=Methods(ping), context=None, request=Request("ping", [1], 1)
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == -32602
    assert response.message == "Invalid params"
    assert response.id == 1


def test_dispatch_request_with_context():
    def ping_with_context(context: Any):
        assert context is sentinel.context
        return Success(None)

    dispatch_request(
        methods=Methods(ping_with_context),
        context=sentinel.context,
        request=Request("ping_with_context", [], 1),
    )
    # Assert is in the method


# create_requests


def test_create_requests():
    requests = create_requests({"jsonrpc": "2.0", "method": "ping"})
    assert isinstance(requests, Request)


def test_create_requests_batch():
    requests = create_requests(
        [{"jsonrpc": "2.0", "method": "ping"}, {"jsonrpc": "2.0", "method": "ping"}],
    )
    assert iter(requests)


# dispatch_to_response_pure


def test_dispatch_to_response_pure():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_to_response_pure_notification():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "ping"}',
    )
    assert response is None


def test_dispatch_to_response_pure_notification_invalid_jsonrpc():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "0", "method": "notify"}',
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_to_response_pure(
        methods=Methods(ping), context=None, deserializer=json.loads, request="{"
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_to_response_pure(
        methods=Methods(ping), context=None, deserializer=json.loads, request="{}"
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_params():
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()

    response = dispatch_to_response_pure(
        methods=Methods(foo),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_params_count():
    def foo(colour: str, size: str):
        pass

    response = dispatch_to_response_pure(
        methods=Methods(foo),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.data == "missing a required argument: 'size'"


# dispatch_to_response


def test_dispatch_to_response():
    response = dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', Methods(ping)
    )
    assert response.result == "pong"


def test_dispatch_to_response_with_global_methods():
    global_methods.items = {}
    global_methods.add(ping)
    response = dispatch_to_response('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response.result == "pong"


# The remaining tests are direct from the examples in the specification


def test_examples_positionals():
    def subtract(minuend, subtrahend):
        return Success(minuend - subtrahend)

    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_examples_nameds():
    def subtract(**kwargs):
        return Success(kwargs["minuend"] - kwargs["subtrahend"])

    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        deserializer=json.loads,
        request='{"jsonrpc": "2.0", "method": "foobar"}',
    )
    assert response is None


def test_examples_invalid_json():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
        request='[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_PARSE_ERROR_CODE


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_to_response_pure(
        request="[]",
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_INVALID_REQUEST_CODE


def test_examples_invalid_jsonrpc_batch():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        methods=Methods(ping), context=None, deserializer=json.loads, request="[1]"
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_INVALID_REQUEST_CODE


def test_examples_multiple_invalid_jsonrpc():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        deserializer=json.loads,
        request="[1, 2, 3]",
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_INVALID_REQUEST_CODE


def test_examples_mixed_requests_and_notifications():
    """
    We break the spec here. The examples put an invalid jsonrpc request in the
    mix here.  but it's removed to test the rest, because we're not validating
    each request individually. Any invalid jsonrpc will respond with a single
    error message.

    The spec example includes this which invalidates the entire request:
        {"foo": "boo"},
    """
    methods = Methods(
        sum=lambda *args: Success(sum(args)),
        notify_hello=lambda *args: Success(19),
        subtract=lambda *args: Success(args[0] - sum(args[1:])),
        get_data=lambda: Success(["hello", 5]),
    )
    requests = json.dumps(
        [
            {"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1"},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
            {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2"},
            {
                "jsonrpc": "2.0",
                "method": "foo.get",
                "params": {"name": "myself"},
                "id": "5",
            },
            {"jsonrpc": "2.0", "method": "get_data", "id": "9"},
        ]
    )
    response = dispatch_to_response_pure(
        methods=methods, context=None, deserializer=json.loads, request=requests
    )
    expected = [
        SuccessResponse(
            result=7, id="1"
        ),  # {"jsonrpc": "2.0", "result": 7, "id": "1"},
        SuccessResponse(
            result=19, id="2"
        ),  # {"jsonrpc": "2.0", "result": 19, "id": "2"},
        ErrorResponse(code=-32601, message="Method not found", data="foo.get", id="5"),
        # {
        #     "jsonrpc": "2.0",
        #     "error": {"code": -32601, "message": "Method not found", "data": "foo.get"},
        #     "id": "5",
        # },
        SuccessResponse(
            result=["hello", 5], id="9"
        ),  # {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
    ]
    assert isinstance(response, list)
    for r in response:
        assert r in expected
