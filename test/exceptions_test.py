"""exceptions_test.py"""
# pylint: disable=missing-docstring,line-too-long

from unittest import TestCase
import json

from jsonrpcserver import exceptions, status


class TestJsonRpcError(TestCase):

    def setUp(self):
        self.e = exceptions.JsonRpcServerError(
            status.HTTP_400_BAD_REQUEST, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT)

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise self.e

    def test_http_status_code(self):
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, self.e.http_status_code)

    def test_response_text(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT
                },
                'id': None
            },
            json.loads(str(self.e))
        )

    def test_response_text_with_request_id(self):
        e = exceptions.JsonRpcServerError(
            status.HTTP_400_BAD_REQUEST, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT, None, 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT
                },
                'id': 1
            },
            json.loads(str(e))
        )

    def test_response_text_with_string_as_data(self):
        e = exceptions.JsonRpcServerError(
            status.HTTP_400_BAD_REQUEST, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT, 'Test', 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': 'Test'
                },
                'id': 1
            },
            json.loads(str(e))
        )

    def test_response_text_with_list_as_data(self):
        e = exceptions.JsonRpcServerError(
            status.HTTP_400_BAD_REQUEST, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT, ['One', 2], 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': ['One', 2]
                },
                'id': 1
            },
            json.loads(str(e))
        )

    def test_response_text_with_dict_as_data(self):
        e = exceptions.JsonRpcServerError(
            status.HTTP_400_BAD_REQUEST, \
            status.JSONRPC_INVALID_REQUEST_CODE, \
            status.JSONRPC_INVALID_REQUEST_TEXT, {'foo': 'bar'}, 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': {'foo': 'bar'}
                },
                'id': 1
            },
            json.loads(str(e))
        )


class TestParseError(TestCase):

    def setUp(self):
        self.e = exceptions.ParseError()

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise self.e

    def test_http_status_code(self):
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, self.e.http_status_code)

    def test_response_text(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_PARSE_ERROR_CODE,
                    'message': status.JSONRPC_PARSE_ERROR_TEXT
                },
                'id': None
            },
            json.loads(str(self.e))
        )


class TestInvalidRequest(TestCase):

    def setUp(self):
        self.e = exceptions.InvalidRequest('Not found')

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise self.e

    def test_http_status_code(self):
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, self.e.http_status_code)

    def test_response_text(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': 'Not found'
                },
                'id': None
            },
            json.loads(str(self.e))
        )

    def test_response_text_with_list_as_data(self):
        e = exceptions.InvalidRequest(['id', 'name'], 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': ['id', 'name']
                },
                'id': 1
            },
            json.loads(str(e))
        )

    def test_response_text_with_dict_as_data(self):
        e = exceptions.InvalidRequest({'id': 'Should be an int', 'name': 'Should be a string'}, 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_REQUEST_CODE,
                    'message': status.JSONRPC_INVALID_REQUEST_TEXT,
                    'data': {'id': 'Should be an int', 'name': 'Should be a string'}
                },
                'id': 1
            },
            json.loads(str(e))
        )


class TestMethodNotFound(TestCase):

    def setUp(self):
        self.e = exceptions.MethodNotFound('get')

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise self.e

    def test_http_status_code(self):
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, self.e.http_status_code)

    def test_response_text(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_METHOD_NOT_FOUND_CODE,
                    'message': status.JSONRPC_METHOD_NOT_FOUND_TEXT,
                    'data': 'get'
                },
                'id': None
            },
            json.loads(str(self.e))
        )

    def test_response_text_with_request_id(self):
        e = exceptions.MethodNotFound('get', 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_METHOD_NOT_FOUND_CODE,
                    'message': status.JSONRPC_METHOD_NOT_FOUND_TEXT,
                    'data': 'get'
                },
                'id': 1
            },
            json.loads(str(e))
        )


class TestInvalidParams(TestCase):

    def setUp(self):
        self.e = exceptions.InvalidParams(['name'])

    def test_raise(self):
        with self.assertRaises(exceptions.JsonRpcServerError):
            raise self.e

    def test_http_status_code(self):
        self.assertEqual(
            status.HTTP_400_BAD_REQUEST, self.e.http_status_code)

    def test_response_text_with_list_as_data(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_PARAMS_CODE,
                    'message': status.JSONRPC_INVALID_PARAMS_TEXT,
                    'data': ['name']
                },
                'id': None
            },
            json.loads(str(exceptions.InvalidParams(['name'])))
        )

    def test_response_text_with_dict_as_data(self):
        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_PARAMS_CODE,
                    'message': status.JSONRPC_INVALID_PARAMS_TEXT,
                    'data': {'name': 'Is missing'}
                },
                'id': None
            },
            json.loads(str(exceptions.InvalidParams({'name': 'Is missing'})))
        )

    def test_response_text_with_request_id(self):
        e = exceptions.InvalidParams(['id'], 1)

        self.assertEqual(
            {
                'jsonrpc': '2.0',
                'error': {
                    'code': status.JSONRPC_INVALID_PARAMS_CODE,
                    'message': status.JSONRPC_INVALID_PARAMS_TEXT,
                    'data': ['id']
                },
                'id': 1
            },
            json.loads(str(e))
        )
