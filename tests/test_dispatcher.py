"""TODO: Add tests for dispatch_requests (non-pure version)"""
import json
from unittest.mock import sentinel

from jsonrpcserver import status
from jsonrpcserver.dispatcher import (
    Context,
    create_requests,
    dispatch_to_response_pure,
    dispatch_request,
    global_schema,
)
from jsonrpcserver.methods import Methods, global_methods
from jsonrpcserver.result import Result, Success
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import ErrorResponse, SuccessResponse


def ping(context: Context) -> Result:
    return Success("pong")


# dispatch_request


def test_dispatch_request_success_result():
    response = dispatch_request(Methods(ping), None, Request("ping", [], 1))
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"


def test_dispatch_request_notification():
    response = dispatch_request(Methods(ping), None, Request("ping", [], NOID))
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

    response = dispatch_request(Methods(fail), None, Request("fail", [], NOID))
    assert response is None


def test_dispatch_request_method_not_found():
    response = dispatch_request(Methods(ping), None, Request("nonexistant", [], 1))
    assert isinstance(response, ErrorResponse)
    assert response.code == -32601
    assert response.message == "Method not found"
    assert response.id == 1


def test_dispatch_request_invalid_params():
    response = dispatch_request(Methods(ping), None, Request("ping", [1], 1))
    assert isinstance(response, ErrorResponse)
    assert response.code == -32602
    assert response.message == "Invalid params"
    assert response.id == 1


def test_dispatch_request_with_extra():
    def ping_with_extra(context: Context):
        assert context.extra is sentinel.extra
        return Success(None)

    dispatch_request(
        Methods(ping_with_extra),
        sentinel.extra,
        Request("ping_with_extra", [], 1),
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


# Dispatch pure


def test_dispatch_to_response_pure():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        extra=None,
        deserializer=json.loads,
        schema=global_schema,
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_to_response_pure_notification():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        extra=None,
        deserializer=json.loads,
        schema=global_schema,
        request='{"jsonrpc": "2.0", "method": "ping"}',
    )
    assert response is None


def test_dispatch_to_response_pure_notification_invalid_jsonrpc():
    response = dispatch_to_response_pure(
        Methods(ping),
        '{"jsonrpc": "0", "method": "notify"}',
        extra=None,
        deserialize=json.loads,
        schema=global_schema,
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_to_response_pure(
        Methods(ping),
        "{",
        extra=None,
        deserialize=default_deserialize,
        schema=global_schema,
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_to_response_pure(
        "{}", Methods(ping), extra=None, deserialize=default_deserialize
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_params():
    def foo(context: Context, colour: str):
        if colour not in ("orange", "red", "yellow"):
            return InvalidParamsResponse(id=context.request.id)

    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
        Methods(foo),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_to_response_pure_invalid_params_count():
    def foo(context: Context, colour: str, size: str):
        pass

    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
        Methods(foo),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert response.data == "missing a required argument: 'size'"


# def test_dispatch_to_response_pure_invalid_params_notification():
#    def foo(bar):
#        if bar < 0:
#            raise InvalidRequestError("bar must be greater than zero")
#    response = dispatch_to_response_pure(str(Notify("foo")), method


# dispatch


def test_dispatch():
    response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', Methods(ping))
    assert response.result == "pong"


def test_dispatch_with_global_methods():
    global_methods.items = {}
    global_methods.add(ping)
    response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response.result == "pong"


def test_dispatch_basic_logging():
    response = dispatch(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        Methods(ping),
        basic_logging=True,
    )


# The remaining tests are direct from the examples in the specification


def test_examples_positionals():
    def subtract(context: Context, minuend, subtrahend):
        return Success(minuend - subtrahend)

    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        Methods(subtract),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
        Methods(subtract),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_examples_nameds():
    def subtract(context: Context, **kwargs):
        return Success(kwargs["minuend"] - kwargs["subtrahend"])

    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
        Methods(subtract),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
        Methods(subtract),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
        Methods(update=lambda: None, foobar=lambda: None),
        extra=None,
        deserialize=default_deserialize,
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        '{"jsonrpc": "2.0", "method": "foobar"}',
        Methods(update=lambda: None, foobar=lambda: None),
        extra=None,
        deserialize=default_deserialize,
    )
    assert response is None


def test_examples_invalid_json():
    response = dispatch_to_response_pure(
        '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
        Methods(ping),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_PARSE_ERROR_CODE


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_to_response_pure(
        "[]",
        Methods(ping),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_INVALID_REQUEST_CODE


def test_examples_invalid_jsonrpc_batch():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        "[1]",
        Methods(ping),
        extra=None,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == status.JSONRPC_INVALID_REQUEST_CODE


def test_examples_multiple_invalid_jsonrpc():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        "[1, 2, 3]",
        Methods(ping),
        extra=None,
        deserialize=default_deserialize,
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
        sum=lambda _, *args: Success(sum(args)),
        notify_hello=lambda _, *args: Success(19),
        subtract=lambda _, *args: Success(args[0] - sum(args[1:])),
        get_data=lambda _: Success(["hello", 5]),
    )
    requests = serialize(
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
        requests,
        methods,
        extra=None,
        deserialize=default_deserialize,
    )
    expected = [
        {"jsonrpc": "2.0", "result": 7, "id": "1"},
        {"jsonrpc": "2.0", "result": 19, "id": "2"},
        {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found", "data": "foo.get"},
            "id": "5",
        },
        {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
    ]
    assert isinstance(response, list)
    for r in response:
        assert r in expected
