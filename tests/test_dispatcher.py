import logging
from json import dumps as serialize
from unittest.mock import sentinel

from jsonrpcserver.dispatcher import (
    Context,
    add_handlers,
    call_requests,
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
    BatchResponse,
    ErrorResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    InvalidParamsResponse,
    MethodNotFoundResponse,
    NotificationResponse,
    SuccessResponse,
)
from jsonrpcserver.exceptions import ApiError


def ping(context: Context):
    return "pong"


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
        debug=True,
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
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, NotificationResponse)


def test_safe_call_notification_failure():
    def fail():
        raise ValueError()

    response = safe_call(
        Request(method="foo", params=[], id=NOID),
        Methods(fail),
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, NotificationResponse)


def test_safe_call_method_not_found():
    response = safe_call(
        Request(method="nonexistant", params=[], id=1),
        Methods(ping),
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, MethodNotFoundResponse)


def test_safe_call_invalid_args():
    response = safe_call(
        Request(method="ping", params=[1], id=1),
        Methods(ping),
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, InvalidParamsResponse)


def test_safe_call_api_error():
    def error(context: Context):
        raise ApiError("Client Error", code=123, data={"data": 42})

    response = safe_call(
        Request(method="error", params=[], id=1),
        Methods(error),
        debug=True,
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
        raise ApiError("Client Error")

    response = safe_call(
        Request(method="error", params=[], id=1),
        Methods(error),
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert isinstance(response, ErrorResponse)
    response_dict = response.deserialized()
    error_dict = response_dict["error"]
    assert error_dict["message"] == "Client Error"
    assert error_dict["code"] == 1
    assert "data" not in error_dict


def test_non_json_encodable_resonse():
    def method(context: Context):
        return b"Hello, World"

    response = safe_call(
        Request(method="method", params=[], id=1),
        Methods(method),
        debug=False,
        extra=None,
        serialize=default_serialize,
    )
    # response must be serializable here
    str(response)
    assert isinstance(response, ErrorResponse)
    response_dict = response.deserialized()
    error_dict = response_dict["error"]
    assert error_dict["message"] == "Server error"
    assert error_dict["code"] == -32000
    assert "data" not in error_dict


# call_requests


def test_call_requests_with_extra():
    def ping_with_extra(context: Context):
        assert context.extra is sentinel.extra

    call_requests(
        Request(method="ping_with_extra", params=[], id=1),
        Methods(ping_with_extra),
        debug=True,
        extra=sentinel.extra,
        serialize=default_serialize,
    )
    # Assert is in the method


def test_call_requests_batch_all_notifications():
    """Should return a BatchResponse response, an empty list"""
    response = call_requests(
        [
            Request(method="notify_sum", params=[1, 2, 4], id=NOID),
            Request(method="notify_hello", params=[7], id=NOID),
        ],
        Methods(ping),
        debug=True,
        extra=None,
        serialize=default_serialize,
    )
    assert str(response) == ""


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
        debug=True,
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
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)


def test_dispatch_pure_notification_invalid_jsonrpc():
    response = dispatch_pure(
        '{"jsonrpc": "0", "method": "notify"}',
        Methods(ping),
        debug=True,
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
        debug=True,
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
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, InvalidJSONRPCResponse)


def test_dispatch_pure_invalid_params():
    def foo(context: Context, colour):
        assert colour in ("orange", "red", "yellow"), "Invalid colour"

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
        Methods(foo),
        debug=True,
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
        debug=True,
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
        return minuend - subtrahend

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        Methods(subtract),
        debug=True,
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
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_examples_nameds():
    def subtract(context: Context, **kwargs):
        return kwargs["minuend"] - kwargs["subtrahend"]

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
        Methods(subtract),
        debug=True,
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
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    methods = {"update": lambda: None, "foobar": lambda: None}
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
        methods,
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foobar"}',
        methods,
        debug=True,
        extra=None,
        serialize=default_serialize,
        deserialize=default_deserialize,
    )
    assert isinstance(response, NotificationResponse)


def test_examples_invalid_json():
    response = dispatch_pure(
        '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
        Methods(ping),
        debug=True,
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
        debug=True,
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
        debug=True,
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
        debug=True,
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
    We break the spec here. The examples put an invalid jsonrpc request in the mix here.
    but it's removed to test the rest, because we're not validating each request
    individually. Any invalid jsonrpc will respond with a single error message.

    The spec example includes this which invalidates the entire request:
        {"foo": "boo"},
    """
    methods = Methods(
        **{
            "sum": lambda _, *args: sum(args),
            "notify_hello": lambda _, *args: 19,
            "subtract": lambda _, *args: args[0] - sum(args[1:]),
            "get_data": lambda _: ["hello", 5],
        }
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
        debug=True,
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
    for r in response.deserialized():
        assert r in expected
