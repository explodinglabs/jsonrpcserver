"""test_exceptions.py"""
from unittest import TestCase, main

from jsonrpcserver.exceptions import JsonRpcServerError, ParseError, \
    InvalidRequest, MethodNotFound, InvalidParams, ServerError


class TestJsonRpcServerError(TestCase):
    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise JsonRpcServerError()


class TestParseError(TestCase):
    def test_raise(self):
        with self.assertRaises(JsonRpcServerError):
            raise ParseError()

    def test_str(self):
        self.assertEqual('Parse error', str(ParseError()))

    def test_configuration(self):
        ParseError.message = 'Error parsing'
        self.assertEqual('Error parsing', str(ParseError()))
        ParseError.message = 'Parse error'


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
