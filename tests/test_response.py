"""
TODO: Test to_json with a non-json-serializable.
TODO: Test to_json with batch responses.
"""
from unittest.mock import sentinel

from jsonrpcserver.request import NOID
from jsonrpcserver.response import (
    ErrorResponse,
    InvalidRequestResponse,
    MethodNotFoundResponse,
    ParseErrorResponse,
    ServerErrorResponse,
    SuccessResponse,
    UNSPECIFIED,
    from_result,
    to_serializable,
)
from jsonrpcserver.result import Success, Error, InvalidParams


def test_SuccessResponse():
    response = SuccessResponse(sentinel.result, sentinel.id)
    assert response.result == sentinel.result
    assert response.id == sentinel.id


def test_ErrorResponse():
    response = ErrorResponse(
        sentinel.code, sentinel.message, sentinel.data, sentinel.id
    )
    assert response.code is sentinel.code
    assert response.message is sentinel.message
    assert response.data is sentinel.data
    assert response.id is sentinel.id


def test_ParseErrorResponse():
    response = ParseErrorResponse(sentinel.data)
    assert response.code == -32700
    assert response.message == "Parse error"
    assert response.data == sentinel.data
    assert response.id == NOID


def test_InvalidRequestResponse():
    response = InvalidRequestResponse(sentinel.data)
    assert response.code == -32600
    assert response.message == "Invalid request"
    assert response.data == sentinel.data
    assert response.id == NOID


def test_MethodNotFoundResponse():
    response = MethodNotFoundResponse(sentinel.data, sentinel.id)
    assert response.code == -32601
    assert response.message == "Method not found"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_InternalErrorResponse():
    response = InternalErrorResponse(sentinel.data, sentinel.id)
    assert response.code == -32603
    assert response.message == "Internal error"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_ServerErrorResponse():
    response = ServerErrorResponse(sentinel.data, sentinel.id)
    assert response.code == -32000
    assert response.message == "Internal error"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_from_result_Success():
    response = from_result(Success(sentinel.result), sentinel.id)
    assert isinstance(response, SuccessResponse) == True
    assert response.result == sentinel.result
    assert response.id == sentinel.id


def test_from_result_Error():
    response = from_result(
        Error(code=sentinel.code, message=sentinel.message, data=sentinel.data),
        sentinel.id,
    )
    assert isinstance(response, ErrorResponse) == True
    assert response.code == sentinel.code
    assert response.message == sentinel.message
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_from_result_InvalidParams():
    response = from_result(InvalidParams(sentinel.message, sentinel.data), sentinel.id,)
    assert isinstance(response, ErrorResponse) == True
    assert response.code == -32602
    assert response.message == sentinel.message
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_from_result_InvalidParams_no_data():
    response = from_result(InvalidParams(sentinel.message), sentinel.id)
    assert isinstance(response, ErrorResponse) == True
    assert response.code == -32602
    assert response.message == sentinel.message
    assert response.data == UNSPECIFIED
    assert response.id == sentinel.id


def test_from_result_notification():
    response = from_result(Success(result=sentinel.result), NOID)
    assert response is None


def test_to_serializable():
    dct = to_serializable(SuccessResponse(sentinel.result, sentinel.id))
    assert dct["jsonrpc"] == "2.0"
    assert dct["result"] == sentinel.result
    assert dct["id"] == sentinel.id


def test_to_serializable_SuccessResponse():
    dct = to_serializable(SuccessResponse(sentinel.result, sentinel.id))
    assert dct["jsonrpc"] == "2.0"
    assert dct["result"] == sentinel.result
    assert dct["id"] == sentinel.id


def test_to_serializable_ErrorResponse():
    dct = to_serializable(
        ErrorResponse(sentinel.code, sentinel.message, sentinel.data, sentinel.id)
    )
    assert dct["jsonrpc"] == "2.0"
    assert dct["error"]["code"] == sentinel.code
    assert dct["error"]["message"] == sentinel.message
    assert dct["error"]["data"] == sentinel.data
    assert dct["id"] == sentinel.id
