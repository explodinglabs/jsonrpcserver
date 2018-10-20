import json

import pytest

from jsonrpcserver import status
from jsonrpcserver.response import (
    BatchResponse,
    ErrorResponse,
    ExceptionResponse,
    InvalidJSONResponse,
    InvalidJSONRPCResponse,
    InvalidParamsResponse,
    MethodNotFoundResponse,
    NotificationResponse,
    Response,
    SuccessResponse,
    sort_dict_response,
)


def test_response():
    with pytest.raises(TypeError):
        Response()  # Abstract


def test_response_http_status():
    class Subclass(Response):
        def wanted():
            return True

    response = Subclass(http_status=1)
    assert response.http_status == 1


def test_notification_response():
    response = NotificationResponse()
    assert response.http_status == 204
    assert response.wanted == False
    assert str(response) == ""


def test_notification_response_str():
    assert str(NotificationResponse()) == ""


def test_batch_response():
    response = BatchResponse(
        {SuccessResponse("foo", id=1), SuccessResponse("bar", id=2)}
    )
    expected = [
        {"jsonrpc": "2.0", "result": "foo", "id": 1},
        {"jsonrpc": "2.0", "result": "bar", "id": 2},
    ]
    assert response.wanted == True
    for r in response.deserialized():
        assert r in expected


def test_sort_dict_response_success():
    response = sort_dict_response({"id": 1, "result": 5, "jsonrpc": "2.0"})
    assert json.dumps(response) == '{"jsonrpc": "2.0", "result": 5, "id": 1}'


def test_sort_dict_response_error():
    response = sort_dict_response(
        {
            "id": 1,
            "error": {
                "data": "bar",
                "message": "foo",
                "code": status.JSONRPC_INVALID_REQUEST_CODE,
            },
            "jsonrpc": "2.0",
        }
    )
    assert (
        json.dumps(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo", "data": "bar"}, "id": 1}'
    )


def test_success_response():
    response = SuccessResponse("foo", id=1)
    assert response.wanted == True
    assert response.result == "foo"
    assert str(response) == '{"jsonrpc": "2.0", "result": "foo", "id": 1}'


def test_success_response_str():
    response = SuccessResponse("foo", id=1)
    assert str(response) == '{"jsonrpc": "2.0", "result": "foo", "id": 1}'


def test_success_response_null_id():
    # OK - any type of id is acceptable
    response = SuccessResponse("foo", id=None)
    assert str(response) == '{"jsonrpc": "2.0", "result": "foo", "id": null}'


def test_success_response_null_result():
    # Perfectly fine.
    response = SuccessResponse(None, id=1)
    assert str(response) == '{"jsonrpc": "2.0", "result": null, "id": 1}'


def test_error_response():
    response = ErrorResponse("foo", id=1, code=-1, debug=True)
    assert response.code == -1
    assert response.message == "foo"
    assert response.wanted == True
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -1, "message": "foo"}, "id": 1}'
    )


def test_error_response_no_id():
    # Responding with an error to a Notification - this is OK; we do respond to
    # notifications under certain circumstances, such as "invalid json" and "invalid
    # json-rpc".
    assert (
        str(ErrorResponse("foo", id=None, code=-1, debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -1, "message": "foo"}, "id": null}'
    )


def test_error_response_data_with_debug_disabled():
    # The data is not included, because debug is False
    assert (
        str(ErrorResponse("foo", id=None, code=-1, data="bar", debug=False))
        == '{"jsonrpc": "2.0", "error": {"code": -1, "message": "foo"}, "id": null}'
    )


def test_error_response_data_with_debug_enabled():
    assert (
        str(ErrorResponse("foo", id=None, code=-1, data="bar", debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -1, "message": "foo", "data": "bar"}, "id": null}'
    )


def test_error_response_http_status():
    response = ErrorResponse(
        "foo", id=1, code=-1, http_status=status.HTTP_BAD_REQUEST, debug=False
    )
    assert response.http_status == status.HTTP_BAD_REQUEST


def test_invalid_json_response():
    assert (
        str(InvalidJSONResponse(data="foo", debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32700, "message": "Invalid JSON", "data": "foo"}, "id": null}'
    )


def test_invalid_jsonrpc_response():
    assert (
        str(InvalidJSONRPCResponse(data="foo", debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid JSON-RPC", "data": "foo"}, "id": null}'
    )


def test_method_not_found_response():
    assert (
        str(MethodNotFoundResponse(id=1, data="foo", debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found", "data": "foo"}, "id": 1}'
    )


def test_invalid_params_response():
    assert (
        str(InvalidParamsResponse(id=1, data="bar", debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid parameters", "data": "bar"}, "id": 1}'
    )


def test_exception_response():
    assert (
        str(ExceptionResponse(ValueError("foo"), id=1, debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "ValueError: foo"}, "id": 1}'
    )


def test_exception_response_with_id():
    assert (
        str(ExceptionResponse(ValueError("foo"), id=1, debug=True))
        == '{"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "ValueError: foo"}, "id": 1}'
    )


def test_exception_response_debug_enabled():
    response = ExceptionResponse(ValueError("There was an error"), id=1, debug=True)
    assert (
        str(response)
        == '{"jsonrpc": "2.0", "error": {"code": -32000, "message": "Server error", "data": "ValueError: There was an error"}, "id": 1}'
    )
