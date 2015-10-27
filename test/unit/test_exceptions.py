"""test_exceptions.py"""
# pylint: disable=missing-docstring

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
        e = ParseError()
        self.assertEqual('Parse error', str(e))

    def test_configuration(self):
        ParseError.message = 'Error parsing'
        e = ParseError()
        self.assertEqual('Error parsing', str(e))
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
