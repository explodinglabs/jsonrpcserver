"""test_exceptions.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main

from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest, MethodNotFound, InvalidParams, ServerError
from jsonrpcserver import status


class TestJsonRpcServerError(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise JsonRpcServerError(
                status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
                status.JSONRPC_INVALID_REQUEST_CODE,
                status.JSONRPC_INVALID_REQUEST_TEXT)

    def test_str(self):
        e = JsonRpcServerError(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT, 'Foo')
        self.assertEqual(status.JSONRPC_INVALID_REQUEST_TEXT, str(e))


class TestParseError(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise ParseError()


class TestInvalidRequest(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise InvalidRequest('foo')


class TestMethodNotFound(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise MethodNotFound('Test')


class TestInvalidParams(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise InvalidParams('Test')


class TestServerError(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise ServerError()


if __name__ == '__main__':
    main()
