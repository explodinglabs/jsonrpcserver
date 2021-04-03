"""TODO: Add tests for dispatch_requests (non-pure version)"""
import logging
from json import dumps as serialize
from unittest.mock import sentinel

from jsonrpcserver.dispatcher import (
    Context,
    add_handlers,
    dispatch_requests_pure,
    create_requests,
    dispatch,
    dispatch_pure,
    log_request,
    log_response,
    remove_handlers,
    safe_call,
    default_deserialize,
    default_serialize,
)
from jsonrpcserver.methods import Methods, global_methods
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import (
    ApiErrorResponse,
    BatchResponse,
    ErrorResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    InvalidParamsResponse,
    MethodNotFoundResponse,
    NotificationResponse,
    SuccessResponse,
)


def ping(context: Context):
    return SuccessResponse("pong", id=context.request.id)


def test_add_handlers():
    add_handlers()


def test_remove_handlers():
    remove_handlers(logging.Handler(), logging.Handler())


def test_log_request():
    log_request("foo")


def test_log_response():
    log_response("foo")


# safe_call


def test_safe_call_success_response():
    response = safe_call(
        Request(method="ping", params=[], id=1),
        Methods(ping),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_safe_call_notification():
    response = safe_call(
        Request(method="ping", params=[], id=NOID),
        Methods(ping),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, NotificationResponse)


def test_safe_call_notification_failure():
    def fail():
        1 / 0

    response = safe_call(
        Request(method="fail", params=[], id=NOID),
        Methods(fail),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, NotificationResponse)


def test_safe_call_method_not_found():
    response = safe_call(
        Request(method="nonexistant", params=[], id=1),
        Methods(ping),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, MethodNotFoundResponse)


def test_safe_call_invalid_args():
    response = safe_call(
        Request(method="ping", params=[1], id=1),
        Methods(ping),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, InvalidParamsResponse)


def test_safe_call_api_error():
    def error(context: Context):
        return ApiErrorResponse(
            "Client Error", code=123, data={"data": 42}, id=context.request.id
        )

    response = safe_call(
        Request(method="error", params=[], id=1),
        Methods(error),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, ErrorResponse)
    error_dict = response.deserialized()["error"]
    assert error_dict["message"] == "Client Error"
    assert error_dict["code"] == 123
    assert error_dict["data"] == {"data": 42}


def test_safe_call_api_error_minimal():
    def error(context: Context):
        return ApiErrorResponse("Client Error", code=123, id=context.request.id)

    response = safe_call(
        Request(method="error", params=[], id=1),
        Methods(error),
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, ErrorResponse)
    response_dict = response.deserialized()
    error_dict = response_dict["error"]
    assert error_dict["message"] == "Client Error"
    assert error_dict["code"] == 123
    assert "data" not in error_dict


# dispatch_requests_pure


def test_dispatch_requests_pure_with_extra():
    def ping_with_extra(context: Context):
        assert context.extra is sentinel.extra

    dispatch_requests_pure(
        Request(method="ping_with_extra", params=[], id=1),
        Methods(ping_with_extra),
        extra=sentinel.extra,
        serialize=default_serialize,
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


def test_dispatch_pure_request():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_pure_notification():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "ping"}',
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)


def test_dispatch_pure_notification_invalid_jsonrpc():
    response = dispatch_pure(
        '{"jsonrpc": "0", "method": "notify"}',
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)


def test_dispatch_pure_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_pure(
        "{",
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidJSONResponse)


def test_dispatch_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_pure(
        "{}",
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidJSONRPCResponse)


def test_dispatch_pure_invalid_params():
    def foo(context: Context, colour: str):
        if colour not in ("orange", "red", "yellow"):
            return InvalidParamsResponse(id=context.request.id)

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
        Methods(foo),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidParamsResponse)


def test_dispatch_pure_invalid_params_count():
    def foo(context: Context, colour: str, size: str):
        pass

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
        Methods(foo),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidParamsResponse)
    assert response.data == "missing a required argument: 'size'"


# def test_dispatch_pure_invalid_params_notification():
#    def foo(bar):
#        if bar < 0:
#            raise InvalidRequestError("bar must be greater than zero")
#    response = dispatch_pure(str(Notify("foo")), method


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
        return SuccessResponse(minuend - subtrahend, id=context.request.id)

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        Methods(subtract),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
        Methods(subtract),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_examples_nameds():
    def subtract(context: Context, **kwargs):
        return SuccessResponse(
            kwargs["minuend"] - kwargs["subtrahend"], id=context.request.id
        )

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
        Methods(subtract),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
        Methods(subtract),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
        Methods(update=lambda: None, foobar=lambda: None),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foobar"}',
        Methods(update=lambda: None, foobar=lambda: None),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)


def test_examples_invalid_json():
    response = dispatch_pure(
        '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Invalid JSON", "data": "Expecting \':\' delimiter: line 1 column 96 (char 95)"}, "id": null}'
    )


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_pure(
        "[]",
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON-RPC", "data": null}, "id": null}'
    )


def test_examples_invalid_jsonrpc_batch():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_pure(
        "[1]",
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidJSONRPCResponse)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON-RPC", "data": null}, "id": null}'
    )


def test_examples_multiple_invalid_jsonrpc():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_pure(
        "[1, 2, 3]",
        Methods(ping),
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, ErrorResponse)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON-RPC", "data": null}, "id": null}'
    )


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
        sum=lambda ctx, *args: SuccessResponse(sum(args), id=ctx.request.id),
        notify_hello=lambda ctx, *args: SuccessResponse(19, id=ctx.request.id),
        subtract=lambda ctx, *args: SuccessResponse(
            args[0] - sum(args[1:]), id=ctx.request.id
        ),
        get_data=lambda ctx: SuccessResponse(["hello", 5], id=ctx.request.id),
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
    response = dispatch_pure(
        requests,
        methods,
        extra=None,
        serialize=default_serialize,
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
    assert isinstance(response, BatchResponse)
    print(response.deserialized())
    for r in response.deserialized():
        assert r in expected
