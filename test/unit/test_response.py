"""test_response.py"""
#pylint:disable=missing-docstring,line-too-long

from unittest import TestCase, main
import json

from jsonrpcserver.response import _sort_response, _Response, SuccessResponse, \
        ErrorResponse
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
            _Response(0, 0).json

    def test_json_debug(self):
        with self.assertRaises(NotImplementedError):
            _Response(0, 0).json_debug

    def test_body(self):
        with self.assertRaises(NotImplementedError):
            _Response(0, 0).body

    def test_body_debug(self):
        with self.assertRaises(NotImplementedError):
            _Response(0, 0).body_debug


class TestSuccessResponse(TestCase):

    def test_no_id_no_result(self):
        # Essentially no id means the request was a notification, so we should
        # return nothing.
        r = SuccessResponse(None, None)
        self.assertEqual(None, r.request_id)
        self.assertEqual('', r.body)
        self.assertEqual(status.HTTP_NO_CONTENT, r.http_status)

    def test_no_id_with_result(self):
        # Notification should not have a result.
        with self.assertRaises(ValueError):
            SuccessResponse(None, 'foo')

    def test_no_result(self):
        r = SuccessResponse(1, None)
        self.assertEqual(None, r.json['result'])

    def test_result_http_status(self):
        r = SuccessResponse(1, 'foo')
        self.assertEqual(200, r.http_status)

    def test_result_number(self):
        r = SuccessResponse(1, 5)
        self.assertEqual(5, r.json['result'])

    def test_result_string(self):
        r = SuccessResponse(1, 'foo')
        self.assertEqual('foo', r.json['result'])

    def test_result_list(self):
        result = ['foo', [1, 2, 3], {'foo': 'bar', 'answer': 42}]
        r = SuccessResponse(1, result)
        self.assertEqual(result, r.json['result'])

    def test_result_dict(self):
        result = {'foo': 'bar', 'answer': 42, 'list': ['One', 2]}
        r = SuccessResponse(1, result)
        self.assertEqual(result, r.json['result'])

    def test_body(self):
        r = SuccessResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}', r.body)

    def test_body_debug_off(self):
        r = SuccessResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}',
                         r.body)

    def test_body_debug_on(self):
        r = SuccessResponse(1, 'foo')
        self.assertEqual('{"jsonrpc": "2.0", "result": "foo", "id": 1}',
                         r.body_debug)


class TestErrorResponse(TestCase):

    def test_no_id(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, None,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo')
        self.assertEqual(None, r.json['id'])

    def test_json(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual({'jsonrpc': '2.0', 'error': {
            'code': -32600, 'message': 'foo'}, 'id': 1}, r.json)

    def test_json_debug_off(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertNotIn('data', r.json['error'])

    def test_json_debug_on(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual('bar', r.json_debug['error']['data'])

    def test_body(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo"}, "id": 1}',
            r.body)

    def test_body_debug_off(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo"}, "id": 1}',
            r.body)

    def test_body_debug_on(self):
        r = ErrorResponse(status.HTTP_BAD_REQUEST, 1,
                          status.JSONRPC_INVALID_REQUEST_CODE, 'foo', 'bar')
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -32600, "message": "foo", "data": "bar"}, "id": 1}',
            r.body_debug)


if __name__ == '__main__':
    main()
