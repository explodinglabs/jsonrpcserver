"""test_py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

from unittest import TestCase, main
import json

from jsonrpcserver.exceptions import *
from jsonrpcserver.status import *


class TestJsonRpcServerError(TestCase):

    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise JsonRpcServerError(JSONRPC_INVALID_REQUEST_HTTP_CODE,
                    JSONRPC_INVALID_REQUEST_CODE, JSONRPC_INVALID_REQUEST_TEXT)

    def test_str(self):
        e = JsonRpcServerError(JSONRPC_INVALID_REQUEST_HTTP_CODE,
                JSONRPC_INVALID_REQUEST_CODE, JSONRPC_INVALID_REQUEST_TEXT,
                'Foo')
        self.assertEqual(JSONRPC_INVALID_REQUEST_TEXT, str(e))


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
