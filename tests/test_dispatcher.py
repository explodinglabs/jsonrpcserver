"""TODO: Add tests for dispatch_requests (non-pure version)"""
from typing import Any
from unittest.mock import sentinel
import json
import pytest

from oslash.either import Left, Right

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
from jsonrpcserver.methods import Methods, global_methods
from jsonrpcserver.request import Request, NOID
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from jsonrpcserver.result import (
    ErrorResult,
    InvalidParamsResult,
    Result,
    SuccessResult,
    NODATA,
)
from jsonrpcserver.utils import identity


# def test_dispatch_to_response_pure_invalid_params_notification():
#    def foo(bar):
#        if bar < 0:
#            raise InvalidRequestError("bar must be greater than zero")
#    response = dispatch_to_response_pure(str(Notify("foo")), method


def ping() -> Result:
    return Right(SuccessResult("pong"))


# to_response


def test_to_response_SuccessResult():
    response = to_response(
        DispatchResult(
            Request("ping", [], sentinel.id), Right(SuccessResult(sentinel.result))
        )
    )
    assert response == Right(SuccessResponse(sentinel.result, sentinel.id))


def test_to_response_ErrorResult():
    response = to_response(
        DispatchResult(
            Request("ping", [], sentinel.id),
            Left(
                ErrorResult(
                    code=sentinel.code, message=sentinel.message, data=sentinel.data
                )
            ),
        ),
    )
    assert response == Left(
        ErrorResponse(sentinel.code, sentinel.message, sentinel.data, sentinel.id)
    )


def test_to_response_InvalidParamsResult():
    response = to_response(
        DispatchResult(
            Request("ping", [], sentinel.id), Left(InvalidParamsResult(sentinel.data))
        )
    )
    assert response == Left(
        ErrorResponse(-32602, "Invalid params", sentinel.data, sentinel.id)
    )


def test_to_response_InvalidParamsResult_no_data():
    response = to_response(
        DispatchResult(Request("ping", [], sentinel.id), Left(InvalidParamsResult()))
    )
    assert response == Left(
        ErrorResponse(-32602, "Invalid params", NODATA, sentinel.id)
    )


def test_to_response_notification():
    with pytest.raises(AssertionError):
        to_response(
            DispatchResult(
                Request("ping", [], NOID), SuccessResult(result=sentinel.result)
            )
        )


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


def test_dispatch_request_success_result():
    request = Request("ping", [], 1)
    assert dispatch_request(Methods(ping), None, request) == DispatchResult(
        request, Right(SuccessResult("pong"))
    )


def test_dispatch_request_notification():
    """Result is still Success, but it won't be converted to a Response."""
    dispatch_result = dispatch_request(Methods(ping), None, Request("ping", [], NOID))
    assert dispatch_result.result == Right(SuccessResult("pong"))


def test_dispatch_request_notification_failure():
    """
    Should not respond. From the spec: Notifications are not confirmable by definition,
    since they do not have a Response object to be returned. As such, the Client would
    not be aware of any errors (like e.g. "Invalid params","Internal error").
    """

    def fail():
        1 / 0

    dispatch_result = dispatch_request(Methods(fail), None, Request("fail", [], NOID))
    assert dispatch_result.result == Left(
        ErrorResult(ERROR_INTERNAL_ERROR, "Internal error", "division by zero")
    )


def test_dispatch_request_method_not_found():
    dispatch_result = dispatch_request(
        Methods(ping), None, Request("nonexistant", [], 1)
    )
    assert dispatch_result.result == Left(
        ErrorResult(ERROR_METHOD_NOT_FOUND, "Method not found", "nonexistant")
    )


def test_dispatch_request_invalid_params():
    dispatch_result = dispatch_request(Methods(ping), None, Request("ping", [1], 1))
    assert dispatch_result.result == Left(
        ErrorResult(
            ERROR_INVALID_PARAMS, "Invalid params", data="too many positional arguments"
        )
    )


def test_dispatch_request_with_context():
    def ping_with_context(context: Any):
        assert context is sentinel.context
        return Right(SuccessResult(None))

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
        post_process=identity,
        context=None,
        methods=Methods(ping),
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    )
    assert response == Right(SuccessResponse("pong", 1))


def test_dispatch_to_response_pure_notification():
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
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
        post_process=identity,
        context=None,
        methods=Methods(ping),
        request="{",
    )
    assert response == Left(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            None,
        )
    )


def test_dispatch_to_response_pure_notification_invalid_jsonrpc():
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(ping),
        request='{"jsonrpc": "0", "method": "notify"}',
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_invalid_jsonrpc():
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(ping),
        request="{}",
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_invalid_params():
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return Left(InvalidParamsResult())

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(foo),
        request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
    )
    assert response == Left(
        ErrorResponse(ERROR_INVALID_PARAMS, "Invalid params", NODATA, 1)
    )


def test_dispatch_to_response_pure_invalid_params_count():
    def foo(colour: str, size: str):
        return Right(SuccessResult())

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(foo),
        request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}, "id": 1}',
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INVALID_PARAMS,
            "Invalid params",
            "missing a required argument: 'size'",
            1,
        )
    )


def test_dispatch_to_response_pure_enforcing_result():
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result():
        return None

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(not_a_result),
        request='{"jsonrpc": "2.0", "method": "not_a_result", "id": 1}',
    )
    assert response == Left(
        ErrorResponse(
            ERROR_INTERNAL_ERROR,
            "Internal error",
            "The method did not return a valid Result",
            1,
        )
    )


def test_dispatch_to_response_pure_raising_exception():
    """Allow raising an exception to return an error."""

    def raise_exception():
        raise JsonRpcError(code=0, message="foo", data="bar")

    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        schema_validator=default_schema_validator,
        post_process=identity,
        context=None,
        methods=Methods(raise_exception),
        request='{"jsonrpc": "2.0", "method": "raise_exception", "id": 1}',
    )
    assert response == Left(ErrorResponse(0, "foo", "bar", 1))


# dispatch_to_response


def test_dispatch_to_response():
    response = dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', Methods(ping)
    )
    assert response == Right(SuccessResponse("pong", 1))


def test_dispatch_to_response_with_global_methods():
    global_methods.items = {}
    global_methods.add(ping)
    response = dispatch_to_response('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response == Right(SuccessResponse("pong", 1))


# The remaining tests are direct from the examples in the specification


def test_examples_positionals():
    def subtract(minuend, subtrahend):
        return Right(SuccessResult(minuend - subtrahend))

    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    )
    assert response == Right(SuccessResponse(19, 1))

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
    )
    assert response == Right(SuccessResponse(-19, 2))


def test_examples_nameds():
    def subtract(**kwargs):
        return Right(SuccessResult(kwargs["minuend"] - kwargs["subtrahend"]))

    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}',
    )
    assert response == Right(SuccessResponse(19, 3))

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(subtract),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}',
    )
    assert response == Right(SuccessResponse(19, 4))


def test_examples_notification():
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        methods=Methods(update=lambda: None, foobar=lambda: None),
        context=None,
        schema_validator=default_schema_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "foobar"}',
    )
    assert response is None


def test_examples_invalid_json():
    response = dispatch_to_response_pure(
        methods=Methods(ping),
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
        methods=Methods(ping),
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
        methods=Methods(ping),
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
        methods=Methods(ping),
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
    methods = Methods(
        sum=lambda *args: Right(SuccessResult(sum(args))),
        notify_hello=lambda *args: Right(SuccessResult(19)),
        subtract=lambda *args: Right(SuccessResult(args[0] - sum(args[1:]))),
        get_data=lambda: Right(SuccessResult(["hello", 5])),
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
