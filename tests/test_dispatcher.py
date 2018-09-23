from unittest import TestCase

from jsonrpcserver.dispatcher import dispatch_request, dispatch_pure
from jsonrpcserver.methods import Methods
from jsonrpcserver.request import Request
from jsonrpcserver.response import (
    BatchResponse,
    ErrorResponse,
    NotificationResponse,
    SuccessResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
)


def foo():
    return "bar"


FOO = object()


def test_log_request():
    pass


def test_log_response():
    pass


def is_batch_request_yes():
    assert is_batch_request([]) is True


def is_batch_request_no():
    assert is_batch_request({}) is False


def test_dispatch_request():
    response = dispatch_request(Request(method="foo"), Methods(foo), debug=True)
    assert isinstance(response, NotificationResponse)


def test_dispatch_request_with_id():
    response = dispatch_request(Request(method="foo", id=1), Methods(foo), debug=True)
    assert isinstance(response, SuccessResponse)
    assert response.result == "bar"
    assert response.id == 1


def test_dispatch_request_batch():
    ...


def test_dispatch_pure():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo"}', Methods(foo), debug=True
    )
    assert isinstance(response, NotificationResponse)


def test_dispatch_pure_with_id():
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo", "id": 1}', Methods(foo), debug=True
    )
    assert isinstance(response, SuccessResponse)


def test_dispatch_pure_with_context():
    def foo_with_context(context=None):
        assert FOO == context
        return "bar"

    res = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "foo_with_context"}',
        Methods(foo_with_context),
        context=FOO,
        debug=True,
    )


def test_dispatch_pure_batch():
    ...


# Notification errors


def test_dispatch_pure_notification_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_pure("{", Methods(foo), debug=True)
    assert isinstance(response, ErrorResponse)


def test_dispatch_pure_notification_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_pure("{}", Methods(foo), debug=True)
    assert isinstance(response, ErrorResponse)


# Request errors


def test_dispatch_pure_invalid_json():
    response = dispatch_pure('{, "id": 1}', Methods(foo), debug=True)
    assert isinstance(response, InvalidJSONResponse)
    assert response.message == "Invalid JSON"


# The following are direct from the examples in the specification


def test_positional_parameters():
    def subtract(minuend, subtrahend):
        return minuend - subtrahend

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
        Methods(subtract),
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
        Methods(subtract),
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == -19


def test_named_parameters():
    def subtract(**kwargs):
        return kwargs["minuend"] - kwargs["subtrahend"]

    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
        Methods(subtract),
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
        Methods(subtract),
        debug=True,
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_notification():
    methods = {"update": lambda: None, "foobar": lambda: None}
    response = dispatch_pure(
        '{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
        methods,
        debug=True,
    )
    assert isinstance(res, NotificationResponse)

    # Second example
    response = dispatch_pure('{"jsonrpc": "2.0", "method": "foobar"}', methods)
    assert isinstance(res, NotificationResponse)


def test_invalid_json():
    response = dispatch_pure(
        Methods(foo),
        '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
        debug=True
    )
    assert isinstance(response, ErrorResponse)
    assert str(response) == '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": nul}'


def test_empty_array():
    response = dispatch_pure('[]', Methods(foo))
    assert isinstance(response, ErrorResponse)
    assert str(response) == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": None}'


def test_invalid_request():
    response = dispatch_pure([foo], [1])
    assert isinstance(response, BatchResponse)
    assert str(response) == '[{"jsonrpc": "2.0", "error": { "code": -32600, "message": "Invalid Request", "data": "1 is not valid under any of the given schemas", }, "id": None}]'


def test_multiple_invalid_requests():
    response = dispatch_pure('[1, 2, 3]', Methods(foo), debug=True)
    assert isinstance(res, BatchResponse)
    assert json.loads(str(response)) == 
        [
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": "1 is not valid under any of the given schemas",
                },
                "id": None,
            },
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": "2 is not valid under any of the given schemas",
                },
                "id": None,
            },
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": "3 is not valid under any of the given schemas",
                },
                "id": None,
            },
        ]


def test_mixed_requests_and_notifications():
    methods = {
            "sum": lambda *args: sum(args),
            "notify_hello": lambda *args: 19,
            "subtract": lambda *args: args[0] - sum(args[1:]),
            "get_data": lambda: ["hello", 5],
    }
    response = dispatch_deserialized(
        [
            {"jsonrpc": "2.0", "method": "sum", "params": [1, 2, 4], "id": "1"},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
            {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": "2"},
            {"foo": "boo"},
            {
                "jsonrpc": "2.0",
                "method": "foo.get",
                "params": {"name": "myself"},
                "id": "5",
            },
            {"jsonrpc": "2.0", "method": "get_data", "id": "9"},
        ],
        methods,
        debug=True
    )
    assert isinstance(response, BatchResponse)
    assert json.loads(str(response)) ==
        [
            {"jsonrpc": "2.0", "result": 7, "id": "1"},
            {"jsonrpc": "2.0", "result": 19, "id": "2"},
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request",
                    "data": "{'foo': 'boo'} is not valid under any of the given schemas",
                },
                "id": None,
            },
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                    "data": "foo.get",
                },
                "id": "5",
            },
            {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
        ]


def test_all_notifications():
    res = dispatch_pure(
        [
            {"jsonrpc": "2.0", "method": "notify_sum", "params": [1, 2, 4]},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        ],
        Methods(foo),
        debug=True
    )
    assert isinstance(response, NotificationResponse)
    assert 
