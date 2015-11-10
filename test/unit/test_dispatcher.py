"""test_dispatcher.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main
import logging

from jsonrpcserver.dispatcher import dispatch, _string_to_dict
from jsonrpcserver.exceptions import ParseError, InvalidParams
from jsonrpcserver import status
from jsonrpcserver.response import ErrorResponse, NotificationResponse, \
    RequestResponse
from jsonrpcserver.request import Request


def foo():
    return 'bar'

class TestStringToDict(TestCase):

    def test_ok(self):
        self.assertEqual({'jsonrpc': '2.0', 'method': 'foo'}, _string_to_dict(
            '{"jsonrpc": "2.0", "method": "foo"}'))

    def test_invalid(self):
        with self.assertRaises(ParseError):
            _string_to_dict('{"jsonrpc": "2.0}')


class TestDispatchNotifications(TestCase):
    """Go easy here, no need to test the _call function"""

    def setUp(self):
        logging.disable(logging.CRITICAL)
        Request.notification_errors = False

    def tearDown(self):
        Request.notification_errors = False

    # Success
    def test_success(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    # Errors
    def test_parse_error(self):
        r = dispatch([foo], '{"jsonrpc')
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Parse error', r['error']['message'])

    def test_errors_disabled(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(r, NotificationResponse)

    def test_errors_enabled(self):
        Request.notification_errors = True
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(r, ErrorResponse)


class TestDispatchRequests(TestCase):
    """Go easy here, no need to test the _call function. Also don't duplicate
    the Notification tests"""

    # Success
    def test(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual('bar', r['result'])
        self.assertEqual(1, r['id'])


class TestDispatchBatch(TestCase):
    """These are direct from the examples in the specification"""

    def test_invalid_json(self):
        r = dispatch(
            [foo],
            '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]')
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}, 'id': None},
            r)

    def test_empty_array(self):
        r = dispatch([foo], [])
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            r)

    def test_invalid_request(self):
        r = dispatch([foo], [1])
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None}],
            r)

    def test_multiple_invalid_requests(self):
        r = dispatch([foo], [1, 2, 3])
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None}],
            r)

    def test_mixed_requests_and_notifications(self):
        r = dispatch(
            {'sum': lambda *args: sum(args), 'notify_hello': lambda *args: 19,
                'subtract': lambda *args: args[0] - sum(args[1:]), 'get_data':
                lambda: ['hello', 5]},
            [{'jsonrpc': '2.0', 'method': 'sum', 'params': [1,2,4], 'id': '1'},
            {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]},
            {'jsonrpc': '2.0', 'method': 'subtract', 'params': [42,23], 'id': '2'},
            {'foo': 'boo'},
            {'jsonrpc': '2.0', 'method': 'foo.get', 'params': {'name': 'myself'}, 'id': '5'},
            {'jsonrpc': '2.0', 'method': 'get_data', 'id': '9'}])
        self.assertEqual(
            [{'jsonrpc': '2.0', 'result': 7, 'id': '1'},
            {'jsonrpc': '2.0', 'result': 19, 'id': '2'},
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': '5'},
            {'jsonrpc': '2.0', 'result': ['hello', 5], 'id': '9'}], r)

    def test_all_notifications(self):
        r = dispatch(
            [foo],
            [{'jsonrpc': '2.0', 'method': 'notify_sum', 'params': [1,2,4]},
            {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]}])
        self.assertIsInstance(r, NotificationResponse)


if __name__ == '__main__':
    main()
