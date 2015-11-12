"""test_response.py"""
# pylint: disable=missing-docstring,line-too-long

from unittest import TestCase, main
import json

from jsonrpcserver.response import _sort_response, RequestResponse, \
    NotificationResponse, ErrorResponse, ExceptionResponse, BatchResponse, \
    _Response
from jsonrpcserver.exceptions import InvalidParams
from jsonrpcserver import status

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
        r = NotificationResponse()
        self.assertEqual('', str(r))
        self.assertEqual(204, r.http_status)


class TestResponse(TestCase):

    def test(self):
        with self.assertRaises(NotImplementedError):
            str(_Response())


class TestRequestResponse(TestCase):

    def test_no_id(self):
        # Not OK - requests must have an id.
        with self.assertRaises(ValueError):
            RequestResponse(None, 'foo')

    def test_no_result(self):
        # Perfectly fine.
        r = RequestResponse(1, None)
        self.assertEqual({'jsonrpc': '2.0', 'result': None, 'id': 1}, r)

    def test(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual({'jsonrpc': '2.0', 'result': 'foo', 'id': 1}, r)

    def test_str(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}', str(r))


class TestErrorResponse(TestCase):

    def setUp(self):
        ErrorResponse.debug = False

    def tearDown(self):
        ErrorResponse.debug = False

    def test(self):
        r = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'foo'}, 'id': 1},
            r)

    def test_str(self):
        r = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo"}, "id": 1}',
            str(r))

    def test_no_id(self):
        # This is OK - we do respond to notifications with certain errors, such
        # as parse error and invalid request.
        r = ErrorResponse(
            status.HTTP_BAD_REQUEST, None, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo')
        self.assertEqual(None, r['id'])

    def test_debug(self):
        ErrorResponse.debug = True
        r = ErrorResponse(
            status.HTTP_BAD_REQUEST, 1, status.JSONRPC_INVALID_REQUEST_CODE,
            'foo', 'bar')
        self.assertEqual('bar', r['error']['data'])


class TestExceptionResponse(TestCase):

    def setUp(self):
        ErrorResponse.debug = False

    def tearDown(self):
        ErrorResponse.debug = False

    def test_jsonrpcservererror(self):
        r = ExceptionResponse(InvalidParams(), None)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': None},
            r)

    def test_non_jsonrpcservererror(self):
        r = ExceptionResponse(ValueError(), None)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32000, 'message': 'Server error'}, 'id': None},
            r)

    def test_with_id(self):
        r = ExceptionResponse(InvalidParams(), 1)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1},
            r)

    def test_with_data(self):
        ErrorResponse.debug = True
        r = ExceptionResponse(InvalidParams('Password missing'), 1)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params', 'data': 'Password missing'}, 'id': 1},
            r)


class TestBatchResponse(TestCase):

    def test(self):
        r = BatchResponse()
        str(r)


if __name__ == '__main__':
    main()
