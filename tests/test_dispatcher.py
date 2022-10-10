"""Test dispatcher.py

TODO: Add tests for dispatch_requests (non-pure version)
"""
from typing import Any, Callable, Dict
from unittest.mock import Mock, patch, sentinel
import json
import pytest

from returns.result import Failure, Success

from jsonrpcserver import Result
from jsonrpcserver.codes import (
    ERROR_INTERNAL_ERROR,
    ERROR_INVALID_PARAMS,
    ERROR_INVALID_REQUEST,
    ERROR_METHOD_NOT_FOUND,
    ERROR_PARSE_ERROR,
    ERROR_SERVER_ERROR,
)
from jsonrpcserver.dispatcher import (
    call,
    create_request,
    dispatch_deserialized,
    dispatch_request,
    dispatch_to_response_pure,
    extract_list,
    extract_args,
    extract_kwargs,
    get_method,
    not_notification,
    to_response,
    validate_args,
    validate_request,
)
from jsonrpcserver.exceptions import JsonRpcError
from jsonrpcserver.main import (
    default_deserializer,
    default_validator,
    dispatch_to_response,
    dispatch,
)
from jsonrpcserver.methods import method
from jsonrpcserver.request import Request
from jsonrpcserver.response import ErrorResponse, SuccessResponse
from jsonrpcserver.result import ErrorResult, InvalidParams, Ok, Result, SuccessResult
from jsonrpcserver.sentinels import NOCONTEXT, NODATA, NOID
from jsonrpcserver.utils import identity

# pylint: disable=missing-function-docstring,missing-class-docstring,too-few-public-methods,unnecessary-lambda-assignment,invalid-name,disallowed-name


def ping() -> Result:
    return Ok("pong")


# extract_list


def test_extract_list() -> None:
    assert extract_list(False, [Success(SuccessResponse("foo", 1))]) == Success(
        SuccessResponse("foo", 1)
    )


def test_extract_list_notification() -> None:
    assert extract_list(False, []) is None


def test_extract_list_batch() -> None:
    assert extract_list(True, [Success(SuccessResponse("foo", 1))]) == [
        Success(SuccessResponse("foo", 1))
    ]


def test_extract_list_batch_all_notifications() -> None:
    assert extract_list(True, []) is None


# to_response


def test_to_response_SuccessResult() -> None:
    assert to_response(
        Request("ping", [], sentinel.id), Success(SuccessResult(sentinel.result))
    ) == Success(SuccessResponse(sentinel.result, sentinel.id))


def test_to_response_ErrorResult() -> None:
    assert (
        to_response(
            Request("ping", [], sentinel.id),
            Failure(
                ErrorResult(
                    code=sentinel.code, message=sentinel.message, data=sentinel.data
                )
            ),
        )
    ) == Failure(
        ErrorResponse(sentinel.code, sentinel.message, sentinel.data, sentinel.id)
    )


def test_to_response_InvalidParams() -> None:
    assert to_response(
        Request("ping", [], sentinel.id), InvalidParams(sentinel.data)
    ) == Failure(ErrorResponse(-32602, "Invalid params", sentinel.data, sentinel.id))


def test_to_response_InvalidParams_no_data() -> None:
    assert to_response(Request("ping", [], sentinel.id), InvalidParams()) == Failure(
        ErrorResponse(-32602, "Invalid params", NODATA, sentinel.id)
    )


def test_to_response_notification() -> None:
    with pytest.raises(AssertionError):
        to_response(
            Request("ping", [], NOID), Success(SuccessResult(result=sentinel.result))
        )


# extract_args


def test_extract_args() -> None:
    assert extract_args(Request("ping", [], NOID), NOCONTEXT) == []


def test_extract_args_with_context() -> None:
    assert extract_args(Request("ping", ["bar"], NOID), "foo") == ["foo", "bar"]


# extract_kwargs


def test_extract_kwargs() -> None:
    assert extract_kwargs(Request("ping", {"foo": "bar"}, NOID)) == {"foo": "bar"}


# validate_result


def test_validate_result_no_arguments() -> None:
    def f() -> Result:
        return Ok()

    assert validate_args(Request("f", [], NOID), NOCONTEXT, f) == Success(f)


def test_validate_result_no_arguments_too_many_positionals() -> None:
    def f() -> Result:
        return Ok()

    assert validate_args(Request("f", ["foo"], NOID), NOCONTEXT, f) == Failure(
        ErrorResult(
            code=ERROR_INVALID_PARAMS,
            message="Invalid params",
            data="too many positional arguments",
        )
    )


def test_validate_result_positionals() -> None:
    def f(x: int) -> Result:
        return Ok()

    assert validate_args(Request("f", [1], NOID), NOCONTEXT, f) == Success(f)


def test_validate_result_positionals_not_passed() -> None:
    def f(x: str) -> Result:
        return Ok()

    assert validate_args(Request("f", {"foo": "bar"}, NOID), NOCONTEXT, f) == Failure(
        ErrorResult(
            ERROR_INVALID_PARAMS, "Invalid params", "missing a required argument: 'x'"
        )
    )


def test_validate_result_keywords() -> None:
    def f(**kwargs: str) -> Result:
        return Ok()

    assert validate_args(Request("f", {"foo": "bar"}, NOID), NOCONTEXT, f) == Success(f)


def test_validate_result_object_method() -> None:
    class FooClass:
        def f(self, *_: str) -> Result:
            return Ok()

    g = FooClass().f
    assert validate_args(Request("g", ["one", "two"], NOID), NOCONTEXT, g) == Success(g)


# call


def test_call() -> None:
    assert call(Request("ping", [], 1), NOCONTEXT, ping) == Success(
        SuccessResult("pong")
    )


def test_call_raising_jsonrpcerror() -> None:
    def method_() -> Result:
        raise JsonRpcError(code=1, message="foo", data=NODATA)

    assert call(Request("ping", [], 1), NOCONTEXT, method_) == Failure(
        ErrorResult(1, "foo")
    )


def test_call_raising_exception() -> None:
    def method_() -> Result:
        raise ValueError("foo")

    assert call(Request("ping", [], 1), NOCONTEXT, method_) == Failure(
        ErrorResult(ERROR_INTERNAL_ERROR, "Internal error", "foo")
    )


# validate_args


@pytest.mark.parametrize(
    "argument,value",
    [
        (
            validate_args(Request("ping", [], 1), NOCONTEXT, ping),
            Success(ping),
        ),
        (
            validate_args(Request("ping", ["foo"], 1), NOCONTEXT, ping),
            Failure(
                ErrorResult(
                    ERROR_INVALID_PARAMS,
                    "Invalid params",
                    "too many positional arguments",
                )
            ),
        ),
    ],
)
def test_validate_args(argument: Result, value: Result) -> None:
    assert argument == value


# get_method


@pytest.mark.parametrize(
    "argument,value",
    [
        (
            get_method({"ping": ping}, "ping"),
            Success(ping),
        ),
        (
            get_method({"ping": ping}, "non-existant"),
            Failure(
                ErrorResult(ERROR_METHOD_NOT_FOUND, "Method not found", "non-existant")
            ),
        ),
    ],
)
def test_get_method(argument: Result, value: Result) -> None:
    assert argument == value


# dispatch_request


def test_dispatch_request() -> None:
    request = Request("ping", [], 1)
    assert dispatch_request({"ping": ping}, NOCONTEXT, request) == (
        request,
        Success(SuccessResult("pong")),
    )


def test_dispatch_request_with_context() -> None:
    def ping_with_context(context: Any) -> Result:
        assert context is sentinel.context
        return Ok()

    dispatch_request(
        {"ping_with_context": ping_with_context},
        sentinel.context,
        Request("ping_with_context", [], 1),
    )
    # Assert is in the method


# create_request


def test_create_request() -> None:
    request = create_request({"jsonrpc": "2.0", "method": "ping"})
    assert isinstance(request, Request)


# not_notification


def test_not_notification() -> None:
    assert not_notification((Request("ping", [], 1), SuccessResult("pong"))) is True


def test_not_notification_false() -> None:
    assert not_notification((Request("ping", [], NOID), SuccessResult("pong"))) is False


# dispatch_deserialized


def test_dispatch_deserialized() -> None:
    assert dispatch_deserialized(
        methods={"ping": ping},
        context=NOCONTEXT,
        post_process=identity,
        deserialized={"jsonrpc": "2.0", "method": "ping", "id": 1},
    ) == Success(SuccessResponse("pong", 1))


# validate_request


def test_validate_request() -> None:
    request = {"jsonrpc": "2.0", "method": "ping"}
    assert validate_request(default_validator, request) == Success(request)


def test_validate_request_invalid() -> None:
    assert validate_request(default_validator, {"jsonrpc": "2.0"}) == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


# dispatch_to_response_pure


def test_dispatch_to_response_pure() -> None:
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request='{"jsonrpc": "2.0", "method": "ping", "id": 1}',
    ) == Success(SuccessResponse("pong", 1))


def test_dispatch_to_response_pure_parse_error() -> None:
    """Unable to parse, must return an error"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="{",
    ) == Failure(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            None,
        )
    )


def test_dispatch_to_response_pure_invalid_request() -> None:
    """Invalid JSON-RPC, must return an error. (impossible to determine if
    notification).
    """
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="{}",
    ) == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_method_not_found() -> None:
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={},
        request='{"jsonrpc": "2.0", "method": "non_existant", "id": 1}',
    ) == Failure(
        ErrorResponse(ERROR_METHOD_NOT_FOUND, "Method not found", "non_existant", 1)
    )


def test_dispatch_to_response_pure_invalid_params_auto() -> None:
    def f(colour: str, size: str) -> Result:  # pylint: disable=unused-argument
        return Ok()

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"f": f},
        request='{"jsonrpc": "2.0", "method": "f", "params": {"colour":"blue"}, "id": 1}',
    ) == Failure(
        ErrorResponse(
            ERROR_INVALID_PARAMS,
            "Invalid params",
            "missing a required argument: 'size'",
            1,
        )
    )


def test_dispatch_to_response_pure_invalid_params_explicitly_returned() -> None:
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()
        return Ok()

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"foo": foo},
        request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"], "id": 1}',
    ) == Failure(ErrorResponse(ERROR_INVALID_PARAMS, "Invalid params", NODATA, 1))


def test_dispatch_to_response_pure_internal_error() -> None:
    def foo() -> Result:
        raise ValueError("foo")

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"foo": foo},
        request='{"jsonrpc": "2.0", "method": "foo", "id": 1}',
    ) == Failure(ErrorResponse(ERROR_INTERNAL_ERROR, "Internal error", "foo", 1))


@patch("jsonrpcserver.dispatcher.dispatch_request", side_effect=ValueError("foo"))
def test_dispatch_to_response_pure_server_error(*_: Mock) -> None:
    def foo() -> Result:
        return Ok()

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"foo": foo},
        request='{"jsonrpc": "2.0", "method": "foo", "id": 1}',
    ) == Failure(ErrorResponse(ERROR_SERVER_ERROR, "Server error", "foo", None))


def test_dispatch_to_response_pure_invalid_result() -> None:
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result() -> Result:
        return None  # type: ignore

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"not_a_result": not_a_result},
        request='{"jsonrpc": "2.0", "method": "not_a_result", "id": 1}',
    ) == Failure(
        ErrorResponse(
            ERROR_INTERNAL_ERROR,
            "Internal error",
            "The method did not return a valid Result (returned None)",
            1,
        )
    )


def test_dispatch_to_response_pure_raising_exception() -> None:
    """Allow raising an exception to return an error."""

    def raise_exception() -> Result:
        raise JsonRpcError(code=0, message="foo", data="bar")

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"raise_exception": raise_exception},
        request='{"jsonrpc": "2.0", "method": "raise_exception", "id": 1}',
    ) == Failure(ErrorResponse(0, "foo", "bar", 1))


# dispatch_to_response_pure -- Notifications


def test_dispatch_to_response_pure_notification() -> None:
    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"ping": ping},
            request='{"jsonrpc": "2.0", "method": "ping"}',
        )
        is None
    )


def test_dispatch_to_response_pure_notification_parse_error() -> None:
    """Unable to parse, must return an error"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="{",
    ) == Failure(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting property name enclosed in double quotes: line 1 column 2 (char 1)",
            None,
        )
    )


def test_dispatch_to_response_pure_notification_invalid_request() -> None:
    """Invalid JSON-RPC, must return an error. (impossible to determine if notification)"""
    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="{}",
    ) == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_dispatch_to_response_pure_notification_method_not_found() -> None:
    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={},
            request='{"jsonrpc": "2.0", "method": "non_existant"}',
        )
        is None
    )


def test_dispatch_to_response_pure_notification_invalid_params_auto() -> None:
    def foo(colour: str, size: str) -> Result:  # pylint: disable=unused-argument
        return Ok()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "params": {"colour":"blue"}}',
        )
        is None
    )


def test_dispatch_to_response_pure_invalid_params_notification_explicitly_returned() -> None:
    def foo(colour: str) -> Result:
        if colour not in ("orange", "red", "yellow"):
            return InvalidParams()
        return Ok()

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo", "params": ["blue"]}',
        )
        is None
    )


def test_dispatch_to_response_pure_notification_internal_error() -> None:
    def foo(bar: str) -> Result:
        raise ValueError

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"foo": foo},
            request='{"jsonrpc": "2.0", "method": "foo"}',
        )
        is None
    )


@patch("jsonrpcserver.dispatcher.dispatch_request", side_effect=ValueError("foo"))
def test_dispatch_to_response_pure_notification_server_error(*_: Mock) -> None:
    def foo() -> Result:
        return Ok()

    assert dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"foo": foo},
        request='{"jsonrpc": "2.0", "method": "foo"}',
    ) == Failure(ErrorResponse(ERROR_SERVER_ERROR, "Server error", "foo", None))


def test_dispatch_to_response_pure_notification_invalid_result() -> None:
    """Methods should return a Result, otherwise we get an Internal Error response."""

    def not_a_result() -> Result:
        return None  # type: ignore

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"not_a_result": not_a_result},
            request='{"jsonrpc": "2.0", "method": "not_a_result"}',
        )
        is None
    )


def test_dispatch_to_response_pure_notification_raising_exception() -> None:
    """Allow raising an exception to return an error."""

    def raise_exception() -> Result:
        raise JsonRpcError(code=0, message="foo", data="bar")

    assert (
        dispatch_to_response_pure(
            deserializer=default_deserializer,
            validator=default_validator,
            post_process=identity,
            context=NOCONTEXT,
            methods={"raise_exception": raise_exception},
            request='{"jsonrpc": "2.0", "method": "raise_exception"}',
        )
        is None
    )


# dispatch_to_response


def test_dispatch_to_response() -> None:
    response = dispatch_to_response(
        '{"jsonrpc": "2.0", "method": "ping", "id": 1}', {"ping": ping}
    )
    assert response == Success(SuccessResponse("pong", 1))


def test_dispatch_to_response_with_global_methods() -> None:
    @method
    def ping() -> Result:  # pylint: disable=redefined-outer-name
        return Ok("pong")

    response = dispatch_to_response('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
    assert response == Success(SuccessResponse("pong", 1))


# The remaining tests are direct from the examples in the specification


def test_examples_positionals() -> None:
    def subtract(minuend: int, subtrahend: int) -> Result:
        return Ok(minuend - subtrahend)

    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}',
    )
    assert response == Success(SuccessResponse(19, 1))

    # Second example
    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}',
    )
    assert response == Success(SuccessResponse(-19, 2))


def test_examples_nameds() -> None:
    def subtract(**kwargs: int) -> Result:
        return Ok(kwargs["minuend"] - kwargs["subtrahend"])

    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request=(
            '{"jsonrpc": "2.0", "method": "subtract", '
            '"params": {"subtrahend": 23, "minuend": 42}, "id": 3}'
        ),
    )
    assert response == Success(SuccessResponse(19, 3))

    # Second example
    response = dispatch_to_response_pure(
        methods={"subtract": subtract},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request=(
            '{"jsonrpc": "2.0", "method": "subtract", '
            '"params": {"minuend": 42, "subtrahend": 23}, "id": 4}'
        ),
    )
    assert response == Success(SuccessResponse(19, 4))


def test_examples_notification() -> None:
    def f() -> Result:
        return Ok()

    response = dispatch_to_response_pure(
        methods={"update": f, "foobar": f},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}',
    )
    assert response is None

    # Second example
    response = dispatch_to_response_pure(
        methods={"update": f, "foobar": f},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request='{"jsonrpc": "2.0", "method": "foobar"}',
    )
    assert response is None


def test_examples_invalid_json() -> None:
    response = dispatch_to_response_pure(
        methods={"ping": ping},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
        request=(
            '[{"jsonrpc": "2.0", "method": "sum", '
            '"params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]'
        ),
    )
    assert response == Failure(
        ErrorResponse(
            ERROR_PARSE_ERROR,
            "Parse error",
            "Expecting ':' delimiter: line 1 column 96 (char 95)",
            None,
        )
    )


def test_examples_empty_array() -> None:
    # This is an invalid JSON-RPC request, should return an error.
    response = dispatch_to_response_pure(
        request="[]",
        methods={"ping": ping},
        context=NOCONTEXT,
        validator=default_validator,
        post_process=identity,
        deserializer=default_deserializer,
    )
    assert response == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_examples_invalid_jsonrpc_batch() -> None:
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="[1]",
    )
    assert response == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_examples_multiple_invalid_jsonrpc() -> None:
    """
    We break the spec here, by not validating each request in the batch individually.
    The examples are expecting a batch response full of error responses.
    """
    response = dispatch_to_response_pure(
        deserializer=default_deserializer,
        validator=default_validator,
        post_process=identity,
        context=NOCONTEXT,
        methods={"ping": ping},
        request="[1, 2, 3]",
    )
    assert response == Failure(
        ErrorResponse(
            ERROR_INVALID_REQUEST,
            "Invalid request",
            "The request failed schema validation",
            None,
        )
    )


def test_examples_mixed_requests_and_notifications() -> None:
    """We break the spec here. The examples put an invalid jsonrpc request in the mix
    here, but it's removed to test the rest, because we're not validating each request
    individually. Any invalid jsonrpc will respond with a single error message.

    The spec example includes this which invalidates the entire request:
        {"foo": "boo"},
    """
    methods = {
        "sum": lambda *args: Ok(sum(args)),
        "notify_hello": lambda *args: Ok(19),
        "subtract": lambda *args: Ok(args[0] - sum(args[1:])),
        "get_data": lambda: Ok(["hello", 5]),
    }
    response = dispatch(
        deserializer=default_deserializer,
        validator=default_validator,
        context=NOCONTEXT,
        methods=methods,
        request="""[
            {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
            {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
            {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
            {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
            {"jsonrpc": "2.0", "method": "get_data", "id": "9"}
        ]""",
    )
    assert json.loads(response) == [
        {"jsonrpc": "2.0", "result": 7, "id": "1"},
        {"jsonrpc": "2.0", "result": 19, "id": "2"},
        {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found", "data": "foo.get"},
            "id": "5",
        },
        {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"},
    ]
