"""test_exceptions.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

from unittest import TestCase, main
import json

from jsonrpcserver import exceptions, status


class TestJsonRpcError(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.JsonRpcServerError(
                status.JSONRPC_INVALID_REQUEST_HTTP_CODE, \
                status.JSONRPC_INVALID_REQUEST_CODE, \
                status.JSONRPC_INVALID_REQUEST_TEXT)

    def test_response_text_with_string_as_data(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_INVALID_REQUEST_CODE,
                'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                'data': 'Test'
            },
            'id': 1
        }, json.loads(str(exceptions.JsonRpcServerError(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT, 'Test', 1))))


class TestParseError(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.ParseError()

    def test_response_text(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_PARSE_ERROR_CODE,
                'message': status.JSONRPC_PARSE_ERROR_TEXT
            },
            'id': None
        }, json.loads(str(exceptions.ParseError())))


class TestInvalidRequest(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.InvalidRequest('Test')

    def test_response_text(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_INVALID_REQUEST_CODE,
                'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                'data': 'Test'
            },
            'id': None
        }, json.loads(str(exceptions.InvalidRequest('Test'))))


class TestMethodNotFound(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.MethodNotFound('Test')

    def test_response(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_METHOD_NOT_FOUND_CODE,
                'message': status.JSONRPC_METHOD_NOT_FOUND_TEXT,
                'data': 'Test'
            },
            'id': None
        }, json.loads(str(exceptions.MethodNotFound('Test'))))


class TestInvalidParams(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.InvalidParams('Test')

    def test_response(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_INVALID_PARAMS_CODE,
                'message': status.JSONRPC_INVALID_PARAMS_TEXT,
                'data': 'name'
            },
            'id': None
        }, json.loads(str(exceptions.InvalidParams('name'))))


class TestServerError(TestCase):

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise exceptions.ServerError()

    def test_response(self):
        self.assertEqual({
            'jsonrpc': '2.0',
            'error': {
                'code': status.JSONRPC_SERVER_ERROR_CODE,
                'message': status.JSONRPC_SERVER_ERROR_TEXT,
                'data': 'Not found'
            },
            'id': None
        }, json.loads(str(exceptions.ServerError(data='Not found'))))


if __name__ == '__main__':
    main()
