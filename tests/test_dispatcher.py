"""TODO: Add tests for dispatch_requests (non-pure version)"""
from typing import Any
from unittest.mock import patch, sentinel
import json
import pytest

from oslash.either import Left, Right

from jsonrpcserver.codes import (
    ERROR_INTERNAL_ERROR,
    ERROR_INVALID_PARAMS,
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
    ERROR_SERVER_ERROR,
)
from jsonrpcserver.dispatcher import (
    create_request,
    dispatch_request,
    dispatch_to_response_pure,
    to_response,
    validate_args,
)
from jsonrpcserver.exceptions import JsonRpcError
from jsonrpcserver.main import (
    default_deserializer,
    default_schema_validator,
    dispatch_to_response,
)
from jsonrpcserver.methods import method
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from jsonrpcserver.result import (
    ErrorResult,
    InvalidParams,
    Result,
    Success,
    SuccessResult,
    NODATA,
)
from jsonrpcserver.utils import identity


def ping() -> Result:
    return Success("pong")


# to_response


def test_to_response_SuccessResult():
    response = to_response(
        Request("ping", [], sentinel.id), Right(SuccessResult(sentinel.result))
    )
    assert response == Right(SuccessResponse(sentinel.result, sentinel.id))


def test_to_response_ErrorResult():
    response = to_response(
        Request("ping", [], sentinel.id),
        Left(
            ErrorResult(
                code=sentinel.code, message=sentinel.message, data=sentinel.data
            )
        ),
    )
    assert response == Left(
        ErrorResponse(sentinel.code, sentinel.message, sentinel.data, sentinel.id)
    )


def test_to_response_InvalidParams():
    response = to_response(
        Request("ping", [], sentinel.id), InvalidParams(sentinel.data)
    )
    assert response == Left(
        ErrorResponse(-32602, "Invalid params", sentinel.data, sentinel.id)
    )


def test_to_response_InvalidParams_no_data():
    response = to_response(Request("ping", [], sentinel.id), InvalidParams())
    assert response == Left(
        ErrorResponse(-32602, "Invalid params", NODATA, sentinel.id)
    )


def test_to_response_notification():
    with pytest.raises(AssertionError):
        to_response(Request("ping", [], NOID), SuccessResult(result=sentinel.result))


# validate_args


def test_validate_no_arguments():
    f = lambda: None
    assert validate_args(Request("f", [], NOID), None, f) == Right(f)


def test_validate_no_arguments_too_many_positionals():
    assert validate_args(Request("f", ["foo"], NOID), None, lambda: None) == Left(
        ErrorResult(
            code=ERROR_INVALID_PARAMS,
            message="Invalid params",
            data="too many positional arguments",
        )
    )


def test_validate_positionals():
    f = lambda x: None
    assert validate_args(Request("f", [1], NOID), None, f) == Right(f)


def test_validate_positionals_not_passed():
    assert validate_args(
        Request("f", {"foo": "bar"}, NOID), None, lambda x: None
    ) == Left(
        ErrorResult(
            ERROR_INVALID_PARAMS, "Invalid params", "missing a required argument: 'x'"
        )
    )


def test_validate_keywords():
    f = lambda **kwargs: None
    assert validate_args(Request("f", {"foo": "bar"}, NOID), None, f) == Right(f)


def test_validate_object_method():
    class FooClass:
        def foo(self, one, two):
            return "bar"

    f = FooClass().foo
    assert validate_args(Request("f", ["one", "two"], NOID), None, f) == Right(f)


# dispatch_request


def test_dispatch_request():
    request = Request("ping", [], 1)
    assert dispatch_request({"ping": ping}, None, request) == (
        request,
        Right(SuccessResult("pong")),
    )


def test_dispatch_request_with_context():
    def ping_with_context(context: Any):
        assert context is sentinel.context
        return Success()

    dispatch_request(
        {"ping_with_context": ping_with_context},
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
    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"ping": ping},
            request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
        )
        == Right(SuccessResponse("pong", 1))
    )


def test_dispatch_to_response_pure_parse_error():
    """Unable to parse, must return an error"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="{",
    ) == Left(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            None,
        )
    )


def test_dispatch_to_response_pure_invalid_request():
    """Invalid JSON-RPC, must return an error. (impossible to determine if
    notification).
    """
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="{}",
    ) == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_method_not_found():
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={},
        request='{"jsonrpc": "2.0", "method": "non_existant", "id": 1}',
    ) == Left(
        ErrorResponse(ERROR_METHOD_NOT_FOUND, "Method not found", "non_existant", 1)
    )


def test_dispatch_to_response_pure_invalid_params_auto():
    def foo(colour: str, size: str):
        return Success()

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"foo": foo},
        request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
    ) == Left(
        ErrorResponse(
            ERROR_INVALID_PARAMS,
            "Invalid params",
            "missing a required argument: 'size'",
            1,
        )
    )


def test_dispatch_to_response_pure_invalid_params_explicitly_returned():
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
        )
        == Left(ErrorResponse(ERROR_INVALID_PARAMS, "Invalid params", NODATA, 1))
    )


def test_dispatch_to_response_pure_internal_error():
    def foo():
        raise ValueError("foo")

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "id": 1}',
        )
        == Left(ErrorResponse(ERROR_INTERNAL_ERROR, "Internal error", "foo", 1))
    )


@patch("jsonrpcserver.dispatcher.dispatch_request", side_effect=ValueError("foo"))
def test_dispatch_to_response_pure_server_error(*_):
    def foo():
        return Success()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "id": 1}',
        )
        == Left(ErrorResponse(ERROR_SERVER_ERROR, "Server error", "foo", None))
    )


def test_dispatch_to_response_pure_invalid_result():
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result():
        return None

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"not_a_result": not_a_result},
        request='{"jsonrpc": "2.0", "method": "not_a_result", "id": 1}',
    ) == Left(
        ErrorResponse(
            ERROR_INTERNAL_ERROR,
            "Internal error",
            "The method did not return a valid Result (returned None)",
            1,
        )
    )


def test_dispatch_to_response_pure_raising_exception():
    """Allow raising an exception to return an error."""

    def raise_exception():
        raise JsonRpcError(code=0, message="foo", data="bar")

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"raise_exception": raise_exception},
            request='{"jsonrpc": "2.0", "method": "raise_exception", "id": 1}',
        )
        == Left(ErrorResponse(0, "foo", "bar", 1))
    )


# dispatch_to_response_pure -- Notifications


def test_dispatch_to_response_pure_notification():
    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"ping": ping},
            request='{"jsonrpc": "2.0", "method": "ping"}',
        )
        == None
    )


def test_dispatch_to_response_pure_notification_parse_error():
    """Unable to parse, must return an error"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="{",
    ) == Left(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            None,
        )
    )


def test_dispatch_to_response_pure_notification_invalid_request():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="{}",
    ) == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_notification_method_not_found():
    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={},
            request='{"jsonrpc": "2.0", "method": "non_existant"}',
        )
        == None
    )


def test_dispatch_to_response_pure_notification_invalid_params_auto():
    def foo(colour: str, size: str):
        return Success()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}}',
        )
        == None
    )


def test_dispatch_to_response_pure_invalid_params_notification_explicitly_returned():
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"]}',
        )
        == None
    )


def test_dispatch_to_response_pure_notification_internal_error():
    def foo(bar):
        raise ValueError

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo"}',
        )
        == None
    )


@patch("jsonrpcserver.dispatcher.dispatch_request", side_effect=ValueError("foo"))
def test_dispatch_to_response_pure_notification_server_error(*_):
    def foo():
        return Success()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo"}',
        )
        == Left(ErrorResponse(ERROR_SERVER_ERROR, "Server error", "foo", None))
    )


def test_dispatch_to_response_pure_notification_invalid_result():
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result():
        return None

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"not_a_result": not_a_result},
            request='{"jsonrpc": "2.0", "method": "not_a_result"}',
        )
        == None
    )


def test_dispatch_to_response_pure_notification_raising_exception():
    """Allow raising an exception to return an error."""

    def raise_exception():
        raise JsonRpcError(code=0, message="foo", data="bar")

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            schema_validator=default_schema_validator,
            post_process=identity,
            context=None,
            methods={"raise_exception": raise_exception},
            request='{"jsonrpc": "2.0", "method": "raise_exception"}',
        )
        == None
    )


# dispatch_to_response


def test_dispatch_to_response():
    response = dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    )
    assert response == Right(SuccessResponse("pong", 1))


def test_dispatch_to_response_with_global_methods():
    @method
    def ping():
        return Success("pong")

    response = dispatch_to_response('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response == Right(SuccessResponse("pong", 1))


# The remaining tests are direct from the examples in the specification


def test_examples_positionals():
    def subtract(minuend, subtrahend):
        return Success(minuend - subtrahend)

    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    )
    assert response == Right(SuccessResponse(19, 1))

    # Second example
    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
    )
    assert response == Right(SuccessResponse(-19, 2))


def test_examples_nameds():
    def subtract(**kwargs):
        return Success(kwargs["minuend"] - kwargs["subtrahend"])

    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
    )
    assert response == Right(SuccessResponse(19, 3))

    # Second example
    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
    )
    assert response == Right(SuccessResponse(19, 4))


def test_examples_notification():
    response = dispatch_to_response_pure(
        methods={"update": lambda: None, "foobar": lambda: None},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        methods={"update": lambda: None, "foobar": lambda: None},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "foobar"}',
    )
    assert response is None


def test_examples_invalid_json():
    response = dispatch_to_response_pure(
        methods={"ping": ping},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]',
    )
    assert response == Left(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting ':' delimiter: line 1 column 96 (char 95)",
            None,
        )
    )


def test_examples_empty_array():
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_to_response_pure(
        request="[]",
        methods={"ping": ping},
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_examples_invalid_jsonrpc_batch():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="[1]",
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_examples_multiple_invalid_jsonrpc():
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods={"ping": ping},
        request="[1, 2, 3]",
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
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
    methods = {
        "sum": lambda *args: Right(SuccessResult(sum(args))),
        "notify_hello": lambda *args: Right(SuccessResult(19)),
        "subtract": lambda *args: Right(SuccessResult(args[0] - sum(args[1:]))),
        "get_data": lambda: Right(SuccessResult(["hello", 5])),
    }
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
        post_process=identity,
        context=None,
        methods=methods,
        request=requests,
    )
    expected = [
        Right(
            SuccessResponse(result=7, id="1")
        ),  # {"jsonrpc": "2.0", "result": 7, "id": "1"},
        Right(
            SuccessResponse(result=19, id="2")
        ),  # {"jsonrpc": "2.0", "result": 19, "id": "2"},
        Left(
            ErrorResponse(
                code=-32601, message="Method not found", data="foo.get", id="5"
            )
        ),
        # {
        #     "jsonrpc": "2.0",
        #     "error": {"code": -32601, "message": "Method not found", "data": "foo.get"},
        #     "id": "5",
        # },
        Right(
            SuccessResponse(result=["hello", 5], id="9")
        ),  # {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
    ]
    # assert isinstance(response, Iterable)
    for r in response:
        assert r in expected
