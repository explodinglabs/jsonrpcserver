"""test_dispatcher.py"""
from unittest import TestCase, main

from jsonrpcserver import config
from jsonrpcserver.dispatcher import dispatch, Requests
from jsonrpcserver.exceptions import ParseError
from jsonrpcserver.response import ErrorResponse, NotificationResponse, RequestResponse, BatchResponse


def foo():
    return 'bar'

FOO = object()


def setUpModule():
    config.debug = True


def tearDownModule():
    config.debug = False


class TestStringToDict(TestCase):
    def test_invalid(self):
        with self.assertRaises(ParseError):
            Requests._string_to_dict('{"jsonrpc": "2.0}')

    def test(self):
        self.assertEqual(
            {'jsonrpc': '2.0', 'method': 'foo'},
            Requests._string_to_dict('{"jsonrpc": "2.0", "method": "foo"}'))

    def test_list(self):
        self.assertEqual(
            [{'jsonrpc': '2.0', 'method': 'foo'}],
            Requests._string_to_dict('[{"jsonrpc": "2.0", "method": "foo"}]'))


class TestDispatchNotifications(TestCase):
    """Go easy here, no need to test the call function"""
    def tearDown(self):
        config.notification_errors = False

    # Success
    def test(self):
        res = dispatch([foo], '{"jsonrpc": "2.0", "method": "foo"}')
        self.assertIsInstance(res, NotificationResponse)

    def test_invalid_str(self):
        # Single quotes around identifiers are invalid!
        res = dispatch([foo], "{'jsonrpc': '2.0', 'method': 'foo'}")
        self.assertIsInstance(res, ErrorResponse)

    def test_object(self):
        res = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(res, NotificationResponse)

    # Errors
    def test_parse_error(self):
        res = dispatch([foo], '{"jsonrpc')
        self.assertIsInstance(res, ErrorResponse)
        self.assertEqual('Parse error', res['error']['message'])

    def test_errors_disabled(self):
        res = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(res, NotificationResponse)

    def test_errors_enabled(self):
        config.notification_errors = True
        res = dispatch([foo], {'jsonrpc': '2.0', 'method': 'non_existant'})
        self.assertIsInstance(res, ErrorResponse)

    # With context
    def test_with_context(self):
        def foo_with_context(context=None):
            self.assertEqual(FOO, context)
            return 'bar'
        res = dispatch([foo_with_context], {'jsonrpc': '2.0', 'method': 'foo_with_context'}, context=FOO)

    def test_batch_with_context(self):
        def foo_with_context(context=None):
            self.assertEqual(FOO, context)
            return 'bar'
        batch_requests = [
            {'jsonrpc': '2.0', 'method': 'foo_with_context'},
            {'jsonrpc': '2.0', 'method': 'foo_with_context'}]
        res = dispatch([foo_with_context], batch_requests, context=FOO)


class TestDispatchRequests(TestCase):
    """Go easy here, no need to test the call function. Also don't duplicate
    the Notification tests"""
    # Success
    def test(self):
        res = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(res, RequestResponse)
        self.assertEqual('bar', res['result'])
        self.assertEqual(1, res['id'])


class TestDispatchSpecificationExamples(TestCase):
    """These are direct from the examples in the specification"""
    def test_positional_parameters(self):
        def subtract(minuend, subtrahend):
            return minuend - subtrahend
        res = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1})
        self.assertIsInstance(res, RequestResponse)
        self.assertEqual({'jsonrpc': '2.0', 'result': 19, 'id': 1}, res)
        # Second example
        res = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2})
        self.assertIsInstance(res, RequestResponse)
        self.assertEqual({'jsonrpc': '2.0', 'result': -19, 'id': 2}, res)

    def test_named_parameters(self):
        def subtract(**kwargs):
            return kwargs['minuend'] - kwargs['subtrahend']
        res = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3})
        self.assertIsInstance(res, RequestResponse)
        self.assertEqual({"jsonrpc": "2.0", "result": 19, "id": 3}, res)
        # Second example
        res = dispatch(
            [subtract],
            {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4})
        self.assertIsInstance(res, RequestResponse)
        self.assertEqual({"jsonrpc": "2.0", "result": 19, "id": 4}, res)

    def notification(self):
        methods = {'update': lambda: None, 'foobar': lambda: None}
        res = dispatch(
            methods,
            {"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]})
        self.assertIsInstance(res, NotificationResponse)
        res = dispatch(methods, {"jsonrpc": "2.0", "method": "foobar"})
        self.assertIsInstance(res, NotificationResponse)

    def test_invalid_json(self):
        res = dispatch(
            [foo],
            '[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"}, {"jsonrpc": "2.0", "method"]')
        self.assertIsInstance(res, ErrorResponse)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32700, 'message': 'Parse error'}, 'id': None},
            res)

    def test_empty_array(self):
        res = dispatch([foo], [])
        self.assertIsInstance(res, ErrorResponse)
        self.assertEqual(
            {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request'}, 'id': None},
            res)

    def test_invalid_request(self):
        res = dispatch([foo], [1])
        self.assertIsInstance(res, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '1 is not valid under any of the given schemas'}, 'id': None}],
            res)

    def test_multiple_invalid_requests(self):
        res = dispatch([foo], [1, 2, 3])
        self.assertIsInstance(res, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '1 is not valid under any of the given schemas'}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '2 is not valid under any of the given schemas'}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': '3 is not valid under any of the given schemas'}, 'id': None}],
            res)

    def test_mixed_requests_and_notifications(self):
        res = dispatch(
            {'sum': lambda *args: sum(args), 'notify_hello': lambda *args: 19,
             'subtract': lambda *args: args[0] - sum(args[1:]), 'get_data':
             lambda: ['hello', 5]},
            [{'jsonrpc': '2.0', 'method': 'sum', 'params': [1, 2, 4], 'id': '1'},
             {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]},
             {'jsonrpc': '2.0', 'method': 'subtract', 'params': [42, 23], 'id': '2'},
             {'foo': 'boo'},
             {'jsonrpc': '2.0', 'method': 'foo.get', 'params': {'name': 'myself'}, 'id': '5'},
             {'jsonrpc': '2.0', 'method': 'get_data', 'id': '9'}])
        self.assertIsInstance(res, BatchResponse)
        self.assertEqual(
            [{'jsonrpc': '2.0', 'result': 7, 'id': '1'},
             {'jsonrpc': '2.0', 'result': 19, 'id': '2'},
             {'jsonrpc': '2.0', 'error': {'code': -32600, 'message': 'Invalid Request', 'data': "{'foo': 'boo'} is not valid under any of the given schemas"}, 'id': None},
             {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found', 'data': 'foo.get'}, 'id': '5'},
             {'jsonrpc': '2.0', 'result': ['hello', 5], 'id': '9'}], res)
        # Response should not the notifications
        self.assertEqual(5, len(res))

    def test_all_notifications(self):
        res = dispatch(
            [foo],
            [{'jsonrpc': '2.0', 'method': 'notify_sum', 'params': [1, 2, 4]},
             {'jsonrpc': '2.0', 'method': 'notify_hello', 'params': [7]}])
        self.assertIsInstance(res, NotificationResponse)


if __name__ == '__main__':
    main()
