from json import loads as deserialize
from unittest.mock import sentinel

from jsonrpcserver.dispatcher import (
    dispatch_request,
    dispatch_deserialized,
    dispatch_pure,
    dispatch,
)
from jsonrpcserver.methods import Methods
from jsonrpcserver.request import Request
from jsonrpcserver.response import (
    BatchResponse,
    ErrorResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    MethodNotFoundResponse,
    InvalidParamsResponse,
    NotificationResponse,
    SuccessResponse,
)


def ping():
    return "pong"


def test_log_request():
    pass


def test_log_response():
    pass


def is_batch_request_yes():
    assert is_batch_request([]) is True


def is_batch_request_no():
    assert is_batch_request({}) is False


# dispatch_request


def test_dispatch_request_success_response():
    response = dispatch_request(Request(method="ping", id=1), Methods(ping), debug=True)
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_request_notification_response():
    response = dispatch_request(Request(method="ping"), Methods(ping), debug=True)
    assert isinstance(response, NotificationResponse)


def test_dispatch_request_method_not_found():
    response = dispatch_request(
        Request(method="nonexistant", id=1), Methods(ping), debug=True
    )
    assert isinstance(response, MethodNotFoundResponse)


def test_dispatch_request_invalid_args():
    response = dispatch_request(
        Request(method="ping", params=[1], id=1), Methods(ping), debug=True
    )
    assert isinstance(response, InvalidParamsResponse)


# dispatch_deserialized


def test_dispatch_deserialized():
    response = dispatch_deserialized(
        {"jsonrpc": "2.0", "method": "ping"},
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, NotificationResponse)


def test_dispatch_deserialized():
    response = dispatch_deserialized(
        {"jsonrpc": "2.0", "method": "ping", "id": 1},
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)


def test_dispatch_deserialized_with_context():
    def ping_with_context(context=None):
        assert context is sentinel.context

    dispatch_deserialized(
        {"jsonrpc": "2.0", "method": "ping_with_context"},
        Methods(ping_with_context),
        context=sentinel.context,
        convert_camel_case=False,
        debug=True,
    )
    # Assert happens in the method


def test_dispatch_deserialized_batch_all_notifications():
    """Should return a Notification response, not batch; as per spec"""
    response = dispatch_deserialized(
        [
            {"jsonrpc": "2.0", "method": "notify_sum", "params": [1, 2, 4]},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        ],
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert str(response) == ""


def test_dispatch_deserialized_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_deserialized(
        {}, Methods(ping), convert_camel_case=False, debug=True
    )
    assert isinstance(response, ErrorResponse)


# Dispatch pure


def test_dispatch_pure_notification():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "ping"}',
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, NotificationResponse)


def test_dispatch_pure_request():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_pure_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_pure("{", Methods(ping), convert_camel_case=False, debug=True)
    assert isinstance(response, InvalidJSONResponse)


def test_dispatch_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_pure("{}", Methods(ping), convert_camel_case=False, debug=True)
    assert isinstance(response, InvalidJSONRPCResponse)


# dispatch


def test_dispatch():
    response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', Methods(ping))
    assert response.result == "pong"


def test_dispatch_with_global_methods():
    methods.items = {}
    methods.add(ping)
    response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response.result == "pong"


# The remaining tests are direct from the examples in the specification


def test_examples_positionals():
    def subtract(minuend, subtrahend):
        return minuend - subtrahend

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        Methods(subtract),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
        Methods(subtract),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_examples_nameds():
    def subtract(**kwargs):
        return kwargs["minuend"] - kwargs["subtrahend"]

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
        Methods(subtract),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
        Methods(subtract),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    methods = {"update": lambda: None, "foobar": lambda: None}
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
        methods,
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, NotificationResponse)

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foobar"}',
        methods,
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, NotificationResponse)


def test_examples_invalid_json():
    response = dispatch_pure(
        '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
        Methods(ping),
        convert_camel_case=False,
        debug=True,
    )
    assert isinstance(response, ErrorResponse)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Invalid JSON", "data": "Expecting \':\' delimiter: line 1 column 96 (char 95)"}, "id": null}'
    )


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_pure("[]", Methods(ping), convert_camel_case=False, debug=True)
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
    response = dispatch_pure("[1]", Methods(ping), convert_camel_case=False, debug=True)
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
        "[1, 2, 3]", Methods(ping), convert_camel_case=False, debug=True
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
            "sum": lambda *args: sum(args),
            "notify_hello": lambda *args: 19,
            "subtract": lambda *args: args[0] - sum(args[1:]),
            "get_data": lambda: ["hello", 5],
        }
    )
    requests = [
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
    response = dispatch_deserialized(
        requests, methods, convert_camel_case=False, debug=True
    )
    assert isinstance(response, BatchResponse)
    assert deserialize(str(response)) == [
        {"jsonrpc": "2.0", "result": 7, "id": "1"},
        {"jsonrpc": "2.0", "result": 19, "id": "2"},
        {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found", "data": "foo.get"},
            "id": "5",
        },
        {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
    ]
