from unittest.mock import sentinel

from oslash.either import Left, Right

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
    assert to_serializable(Right(SuccessResponse(sentinel.result, sentinel.id))) == {
        "jsonrpc": "2.0",
        "result": sentinel.result,
        "id": sentinel.id,
    }


def test_to_serializable_None():
    assert to_serializable(None) == None


def test_to_serializable_SuccessResponse():
    assert to_serializable(Right(SuccessResponse(sentinel.result, sentinel.id))) == {
        "jsonrpc": "2.0",
        "result": sentinel.result,
        "id": sentinel.id,
    }


def test_to_serializable_ErrorResponse():
    assert to_serializable(
        Left(ErrorResponse(sentinel.code, sentinel.message, sentinel.data, sentinel.id))
    ) == {
        "jsonrpc": "2.0",
        "error": {
            "code": sentinel.code,
            "message": sentinel.message,
            "data": sentinel.data,
        },
        "id": sentinel.id,
    }


def test_to_serializable_list():
    assert to_serializable([Right(SuccessResponse(sentinel.result, sentinel.id))]) == [
        {
            "jsonrpc": "2.0",
            "result": sentinel.result,
            "id": sentinel.id,
        }
    ]
