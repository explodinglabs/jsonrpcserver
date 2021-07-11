"""TODO: Add tests for dispatch_requests (non-pure version)"""
import json
import pytest
from typing import Any
from unittest.mock import sentinel

from jsonrpcserver.codes import (
    ERROR_INTERNAL_ERROR,
    ERROR_INVALID_PARAMS,
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
)
from jsonrpcserver.dispatcher import (
    DispatchResult,
    create_request,
    default_deserializer,
    default_schema_validator,
    dispatch_request,
    dispatch_to_response,
    dispatch_to_response_pure,
    from_result,
    validate_args,
)
from jsonrpcserver.exceptions import JsonRpcError
from jsonrpcserver.methods import Methods, global_methods
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from jsonrpcserver.result import (
    Error,
    InvalidParams,
    Result,
    Success,
    UNSPECIFIED,
)


# def test_dispatch_to_response_pure_invalid_params_notification():
#    def foo(bar):
#        if bar < 0:
#            raise InvalidRequestError("bar must be greater than zero")
#    response = dispatch_to_response_pure(str(Notify("foo")), method


def ping() -> Result:
    return Success("pong")


# from_result


def test_from_result_Success():
    response = from_result(
        DispatchResult(Request("ping", [], sentinel.id), Success(sentinel.result))
    )
    assert isinstance(response, SuccessResponse) == True
    assert response.result == sentinel.result
    assert response.id == sentinel.id


def test_from_result_Error():
    response = from_result(
        DispatchResult(
            Request("ping", [], sentinel.id),
            Error(code=sentinel.code, message=sentinel.message, data=sentinel.data),
        ),
    )
    assert isinstance(response, ErrorResponse) == True
    assert response.code == sentinel.code
    assert response.message == sentinel.message
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_from_result_InvalidParams():
    response = from_result(
        DispatchResult(Request("ping", [], sentinel.id), InvalidParams(sentinel.data))
    )
    assert isinstance(response, ErrorResponse) == True
    assert response.code == -32602
    assert response.message == "Invalid params"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_from_result_InvalidParams_no_data():
    response = from_result(
        DispatchResult(Request("ping", [], sentinel.id), InvalidParams())
    )
    assert isinstance(response, ErrorResponse) == True
    assert response.code == -32602
    assert response.message == "Invalid params"
    assert response.data == UNSPECIFIED
    assert response.id == sentinel.id


def test_from_result_notification():
    with pytest.raises(AssertionError):
        from_result(
            DispatchResult(Request("ping", [], NOID), Success(result=sentinel.result))
        )


# validate_args


def test_validate_no_arguments():
    f = lambda: None
    assert validate_args(f) == Success(f)


def test_validate_no_arguments_too_many_positionals():
    result = validate_args(lambda: None, "foo")
    assert result.code == ERROR_INVALID_PARAMS
    assert result.data == "too many positional arguments"


def test_validate_positionals():
    f = lambda x: None
    assert validate_args(f, 1) == Success(f)


def test_validate_positionals_not_passed():
    f = lambda x: None
    result = validate_args(f, foo="bar")
    assert result.code == ERROR_INVALID_PARAMS
    assert result.data == "missing a required argument: 'x'"


def test_validate_keywords():
    f = lambda **kwargs: None
    result = validate_args(f, foo="bar")
    assert result == Success(f)


def test_validate_object_method():
    class FooClass:
        def foo(self, one, two):
            return "bar"

    f = FooClass().foo
    result = validate_args(f, "one", "two")
    assert result == Success(f)


# dispatch_request


def test_dispatch_request_success_result():
    dispatch_result = dispatch_request(Methods(ping), None, Request("ping", [], 1))
    assert dispatch_result.result.result == "pong"


def test_dispatch_request_notification():
    """Result is still Success, but it won't be converted to a Response."""
    dispatch_result = dispatch_request(Methods(ping), None, Request("ping", [], NOID))
    assert isinstance(dispatch_result.result, Success)


def test_dispatch_request_notification_failure():
    """
    Should not respond. From the spec: Notifications are not confirmable by definition,
    since they do not have a Response object to be returned. As such, the Client would
    not be aware of any errors (like e.g. "Invalid params","Internal error").
    """

    def fail():
        1 / 0

    dispatch_result = dispatch_request(Methods(fail), None, Request("fail", [], NOID))
    assert isinstance(dispatch_result.result, Error)
    assert dispatch_result.result.code == ERROR_INTERNAL_ERROR


def test_dispatch_request_method_not_found():
    dispatch_result = dispatch_request(
        Methods(ping), None, Request("nonexistant", [], 1)
    )
    assert isinstance(dispatch_result.result, Error)
    assert dispatch_result.result.code == ERROR_METHOD_NOT_FOUND


def test_dispatch_request_invalid_params():
    dispatch_result = dispatch_request(Methods(ping), None, Request("ping", [1], 1))
    assert isinstance(dispatch_result.result, Error)
    assert dispatch_result.result.code == ERROR_INVALID_PARAMS


def test_dispatch_request_with_context():
    def ping_with_context(context: Any):
        assert context is sentinel.context
        return Success(None)

    dispatch_request(
        Methods(ping_with_context),
        sentinel.context,
        Request("ping_with_context", [], 1),
    )
    # Assert is in the method


# create_requests


def test_create_request():
    request = create_request({"jsonrpc": "2.0", "method": "ping"})
    assert isinstance(request, Request)


# dispatch_to_response_pure


def test_dispatch_to_response_pure():
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == "pong"
    assert response.id == 1


def test_dispatch_to_response_pure_notification():
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request='{"jsonrpc": "2.0", "method": "ping"}',
    )
    assert response is None


def test_dispatch_to_response_pure_invalid_json():
    """Unable to parse, must return an error"""
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request="{",
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_PARSE_ERROR


def test_dispatch_to_response_pure_notification_invalid_jsonrpc():
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request='{"jsonrpc": "0", "method": "notify"}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_REQUEST


def test_dispatch_to_response_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request="{}",
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_REQUEST


def test_dispatch_to_response_pure_invalid_params():
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(foo),
        request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_PARAMS


def test_dispatch_to_response_pure_invalid_params_count():
    def foo(colour: str, size: str):
        pass

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(foo),
        request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_PARAMS


def test_dispatch_to_response_pure_enforcing_result():
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result():
        return None

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(not_a_result),
        request='{"jsonrpc": "2.0", "method": "not_a_result", "id": 1}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INTERNAL_ERROR
    assert response.data == "The method did not return a Result"


def test_dispatch_to_response_pure_raising_exception():
    """Allow raising an exception to return an error."""

    def raise_exception():
        raise JsonRpcError(code=0, message="foo", data="bar")

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(raise_exception),
        request='{"jsonrpc": "2.0", "method": "raise_exception", "id": 1}',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == 0
    assert response.message == "foo"
    assert response.data == "bar"


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
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
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
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
    )
    assert isinstance(response, SuccessResponse)
    assert response.result == 19


def test_examples_notification():
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "foobar"}',
    )
    assert response is None


def test_examples_invalid_json():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
        request='[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_PARSE_ERROR


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_to_response_pure(
        request="[]",
        methods=Methods(ping),
        context=None,
        schema_validator=default_schema_validator,
        deserializer=default_deserializer,
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_REQUEST


def test_examples_invalid_jsonrpc_batch():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request="[1]",
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_REQUEST


def test_examples_multiple_invalid_jsonrpc():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=Methods(ping),
        request="[1, 2, 3]",
    )
    assert isinstance(response, ErrorResponse)
    assert response.code == ERROR_INVALID_REQUEST


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
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        context=None,
        methods=methods,
        request=requests,
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
    # assert isinstance(response, Iterable)
    for r in response:
        assert r in expected
