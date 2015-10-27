"""test_response.py"""
# pylint: disable=missing-docstring,line-too-long

from unittest import TestCase, main
import json

from jsonrpcserver.response import _sort_response, _Response, RequestResponse, \
    NotificationResponse, ErrorResponse
from jsonrpcserver import status

class TestSortResponse(TestCase):

    def test_sort_response_success(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "result": 5, "id": 1}',
            json.dumps(_sort_response({'id': 1, 'result': 5, 'jsonrpc': '2.0'}))
        )

    def test_sort_response_error(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo", "data": "bar"}, "id": 1}',
            json.dumps(_sort_response({'id': 1, 'error': {
                'data': 'bar', 'message': 'foo', 'code':
                status.JSONRPC_INVALID_REQUEST_CODE}, 'jsonrpc': '2.0'})),
        )


class TestResponse(TestCase):
    # pylint: disable=expression-not-assigned

    def test_json(self):
        with self.assertRaises(NotImplementedError):
            _Response(0).json

    def test_json_debug(self):
        with self.assertRaises(NotImplementedError):
            _Response(0).json_debug

    def test_body(self):
        with self.assertRaises(NotImplementedError):
            _Response(0).body

    def test_body_debug(self):
        with self.assertRaises(NotImplementedError):
            _Response(0).body_debug


class TestErrorResponse(TestCase):

    def test_no_id(self):
        # This is OK - we will respond to notifications with errors, such as
        # parse error and invalid request.
        r = ErrorResponse(status.HTTP_BAD_REQUEST, None,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo')
        self.assertEqual(None, r.json['id'])

    def test_json(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual({'jsonrpc': '2.0', 'error': {
            'code': -32600, 'message': 'foo'}, 'id': 1}, r.json)

    def test_json_debug(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual('bar', r.json_debug['error']['data'])

    def test_body(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo"}, "id": 1}',
            r.body)

    def test_body_debug(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo", "data": "bar"}, "id": 1}',
            r.body_debug)


class TestRequestResponse(TestCase):

    def test_no_id(self):
        # Not OK - requests must have an id.
        with self.assertRaises(ValueError):
            RequestResponse(None, 'foo')

    def test_no_result(self):
        # Perfectly fine.
        r = RequestResponse(1, None)
        self.assertEqual({'jsonrpc': '2.0', 'result': None, 'id': 1}, r.json)

    def test_json(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual({'jsonrpc': '2.0', 'result': 'foo', 'id': 1}, r.json)

    def test_json_debug(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual(
            {'jsonrpc': '2.0', 'result': 'foo', 'id': 1}, r.json_debug)

    def test_body(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}', r.body)

    def test_body_debug(self):
        r = RequestResponse(1, 'foo')
        self.assertEqual(
            '{"jsonrpc": "2.0", "result": "foo", "id": 1}', r.body_debug)


class TestNotificationResponse(TestCase):

    def test(self):
        r = NotificationResponse()
        self.assertEqual(None, r.json)
        self.assertEqual(None, r.json_debug)
        self.assertEqual('', r.body)
        self.assertEqual('', r.body_debug)
        self.assertEqual(204, r.http_status)


if __name__ == '__main__':
    main()
