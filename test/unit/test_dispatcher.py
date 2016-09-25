"""test_dispatcher.py"""
# pylint: disable=missing-docstring,line-too-long

from unittest import TestCase, main

from jsonrpcserver.dispatcher import dispatch, _string_to_dict
from jsonrpcserver.exceptions import ParseError
from jsonrpcserver.response import ErrorResponse, NotificationResponse, \
    RequestResponse, BatchResponse
from jsonrpcserver import config

def setUpModule():
    config.debug = True

def tearDownModule():
    config.debug = False

def foo(): # pylint: disable=blacklisted-name
    return 'bar'

class TestStringToDict(TestCase):

    def test_invalid(self):
        with self.assertRaises(ParseError):
            _string_to_dict('{"jsonrpc": "2.0}')

    def test(self):
        self.assertEqual(
            {'jsonrpc': '2.0', 'method': 'foo'},
            _string_to_dict('{"jsonrpc": "2.0", "method": "foo"}'))

    def test_list(self):
        self.assertEqual(
            [{'jsonrpc': '2.0', 'method': 'foo'}],
            _string_to_dict('[{"jsonrpc": "2.0", "method": "foo"}]'))


class TestDispatchNotifications(TestCase):
    """Go easy here, no need to test the call function"""

    def tearDown(self):
        config.notification_errors = False

    # Success
    def test(self):
        r = dispatch([foo], '{"jsonrpc": "2.0", "method": "foo"}')
        self.assertIsInstance(r, NotificationResponse)

    def test_invalid_str(self):
        # Single quotes around identifiers are invalid!
        r = dispatch([foo], "{'jsonrpc': '2.0', 'method': 'foo'}")
        self.assertIsInstance(r, ErrorResponse)

    def test_object(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    # Errors
    def test_parse_error(self):
        r = dispatch([foo], '{"jsonrpc')
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Parse error', r['error']['message'])

    def test_notification_errors_disabled(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(r, NotificationResponse)

    def test_notification_errors_enabled(self):
        config.notification_errors = True
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(r, ErrorResponse)


class TestDispatchRequests(TestCase):
    """Go easy here, no need to test the call function. Also don't duplicate
    the Notification tests"""

    # Success
    def test(self):
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual('bar', r['result'])
        self.assertEqual(1, r['id'])


class TestDispatchSpecificationExamples(TestCase):
    """These are direct from the examples in the specification"""

    def test_positional_parameters(self):
        def subtract(x, y):
            return x - y
        r = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual({'jsonrpc': '2.0', 'result': 19, 'id': 1}, r)
        # Second example
        r = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual({'jsonrpc': '2.0', 'result': -19, 'id': 2}, r)

    def test_named_parameters(self):
        def subtract(**kwargs):
            return kwargs['minuend'] - kwargs['subtrahend']
        r = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual({"jsonrpc": "2.0", "result": 19, "id": 3}, r)
        # Second example
        r = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual({"jsonrpc": "2.0", "result": 19, "id": 4}, r)

    def notification(self):
        methods = {'update': lambda: None, 'foobar': lambda: None}
        r = dispatch(
            methods,
            {"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]})
        self.assertIsInstance(r, NotificationResponse)
        r = dispatch(methods, {"jsonrpc": "2.0", "method": "foobar"})
        self.assertIsInstance(r, NotificationResponse)

    def test_invalid_json(self):
        r = dispatch(
            [foo],
            '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]')
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}, 'id': None},
            r)

    def test_empty_array(self):
        r = dispatch([foo], [])
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            r)

    def test_invalid_request(self):
        r = dispatch([foo], [1])
        self.assertIsInstance(r, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '1 is not valid under any of the given schemas'}, 'id': None}],
            r)

    def test_multiple_invalid_requests(self):
        r = dispatch([foo], [1, 2, 3])
        self.assertIsInstance(r, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '1 is not valid under any of the given schemas'}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '2 is not valid under any of the given schemas'}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '3 is not valid under any of the given schemas'}, 'id': None}],
            r)

    def test_mixed_requests_and_notifications(self):
        r = dispatch(
            {'sum': lambda *args: sum(args), 'notify_hello': lambda *args: 19,
             'subtract': lambda *args: args[0] - sum(args[1:]), 'get_data':
             lambda: ['hello', 5]},
            [{'jsonrpc': '2.0', 'method': 'sum', 'params': [1, 2, 4], 'id': '1'},
             {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]},
             {'jsonrpc': '2.0', 'method': 'subtract', 'params': [42, 23], 'id': '2'},
             {'foo': 'boo'},
             {'jsonrpc': '2.0', 'method': 'foo.get', 'params': {'name': 'myself'}, 'id': '5'},
             {'jsonrpc': '2.0', 'method': 'get_data', 'id': '9'}])
        self.assertIsInstance(r, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'result': 7, 'id': '1'},
             {'jsonrpc': '2.0', 'result': 19, 'id': '2'},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': "{'foo': 'boo'} is not valid under any of the given schemas"}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found', 'data': 'foo.get'}, 'id': '5'},
             {'jsonrpc': '2.0', 'result': ['hello', 5], 'id': '9'}], r)

    def test_all_notifications(self):
        r = dispatch(
            [foo],
            [{'jsonrpc': '2.0', 'method': 'notify_sum', 'params': [1, 2, 4]},
             {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]}])
        self.assertIsInstance(r, NotificationResponse)


if __name__ == '__main__':
    main()
