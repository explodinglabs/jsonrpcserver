from unittest.mock import sentinel

from jsonrpcserver.response import (
    ErrorResponse,
    InvalidRequestResponse,
    MethodNotFoundResponse,
    ParseErrorResponse,
    ServerErrorResponse,
    SuccessResponse,
    to_serializable,
)


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
    assert response.id == None


def test_InvalidRequestResponse():
    response = InvalidRequestResponse(sentinel.data)
    assert response.code == -32600
    assert response.message == "Invalid request"
    assert response.data == sentinel.data
    assert response.id == None


def test_MethodNotFoundResponse():
    response = MethodNotFoundResponse(sentinel.data, sentinel.id)
    assert response.code == -32601
    assert response.message == "Method not found"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


def test_ServerErrorResponse():
    response = ServerErrorResponse(sentinel.data, sentinel.id)
    assert response.code == -32000
    assert response.message == "Server error"
    assert response.data == sentinel.data
    assert response.id == sentinel.id


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
