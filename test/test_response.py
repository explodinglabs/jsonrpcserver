"""test_response.py"""
from unittest import TestCase, main
import json

from jsonrpcserver import config, status
from jsonrpcserver.exceptions import InvalidParams
from jsonrpcserver.response import (
    _sort_response, Response, RequestResponse, NotificationResponse,
    ErrorResponse, ExceptionResponse, BatchResponse)


class TestSortResponse(TestCase):
    def test_sort_response_success(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "result": 5, "id": 1}',
            json.dumps(_sort_response({'id': 1, 'result': 5, 'jsonrpc': '2.0'})))

    def test_sort_response_error(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo", "data": "bar"}, "id": 1}',
            json.dumps(_sort_response({'id': 1, 'error': {'data': 'bar', 'message': 'foo', 'code': status.JSONRPC_INVALID_REQUEST_CODE}, 'jsonrpc': '2.0'})))


class TestNotificationResponse(TestCase):
    def test(self):
        response = NotificationResponse()
        self.assertEqual('', str(response))
        self.assertEqual(204, response.http_status)

    def test_str(self):
        response = NotificationResponse()
        self.assertEqual('', str(response))


class TestResponse(TestCase):
    def test(self):
        with self.assertRaises(NotImplementedError):
            str(Response())


class TestRequestResponse(TestCase):
    def test_no_id(self):
        # Not OK - requests must have an id.
        with self.assertRaises(ValueError):
            RequestResponse(None, 'foo')

    def test_no_result(self):
        # Perfectly fine.
        response = RequestResponse(1, None)
        self.assertEqual({'jsonrpc': '2.0', 'result': None, 'id': 1}, response)

    def test(self):
        response = RequestResponse(1, 'foo')
        self.assertEqual({'jsonrpc': '2.0', 'result': 'foo', 'id': 1}, response)

    def test_str(self):
        response = RequestResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}', str(response))


class TestErrorResponse(TestCase):
    def setUp(self):
        config.debug = False

    def tearDown(self):
        config.debug = False

    def test(self):
        response = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'foo'}, 'id': 1},
            response)

    def test_str(self):
        response = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo"}, "id": 1}',
            str(response))

    def test_no_id(self):
        # This is OK - we do respond to notifications with certain errors, such
        # as parse error and invalid request.
        response = ErrorResponse(
            status.HTTP_BAD_REQUEST, None, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo')
        self.assertEqual(None, response['id'])

    def test_debug(self):
        config.debug = True
        response = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual('bar', response['error']['data'])


class TestExceptionResponse(TestCase):
    def setUp(self):
        config.debug = False

    def tearDown(self):
        config.debug = False

    def test_jsonrpcservererror(self):
        response = ExceptionResponse(InvalidParams(), None)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': None},
            response)

    def test_non_jsonrpcservererror(self):
        response = ExceptionResponse(ValueError(), None)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32000, 'message': 'Server error'}, 'id': None},
            response)

    def test_with_id(self):
        response = ExceptionResponse(InvalidParams(), 1)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1},
            response)

    def test_with_data(self):
        config.debug = True
        response = ExceptionResponse(InvalidParams('Password missing'), 1)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params', 'data': 'Password missing'}, 'id': 1},
            response)


class TestBatchResponse(TestCase):
    def test(self):
        str(BatchResponse())


if __name__ == '__main__':
    main()
