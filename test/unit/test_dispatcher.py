"""test_dispatcher.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main
import logging

from jsonrpcserver.dispatcher import dispatch, _string_to_dict
from jsonrpcserver.exceptions import ParseError, InvalidParams
from jsonrpcserver import status
from jsonrpcserver.response import ErrorResponse, NotificationResponse, \
    RequestResponse


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

    # Success
    def test_success(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    # Errors - note that parse error and invalid requests *always* get response
    def test_parse_error(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc')
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Parse error', r.json['error']['message'])

    def test_invalid_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0'})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Invalid request', r.json['error']['message'])

    def test_method_not_found(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'baz'})
        self.assertIsInstance(r, NotificationResponse)

    def test_invalid_params(self):
        def foo(x): # pylint: disable=unused-argument
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    def test_explicitly_raised_exception(self):
        def foo():
            raise InvalidParams()
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    def test_uncaught_exception(self):
        def foo():
            return 1/0
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertIsInstance(r, NotificationResponse)

    # Configuration
    def test_config_notification_errors_on(self):
        # Should return "method not found" error
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'baz'},
                     notification_errors=True)
        self.assertIsInstance(r, ErrorResponse)

    def test_configuring_http_status(self):
        def foo():
            return 'bar'
        NotificationResponse.http_status = status.HTTP_OK
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual(status.HTTP_OK, r.http_status)
        NotificationResponse.http_status = status.HTTP_NO_CONTENT


class TestDispatchRequests(TestCase):
    """Go easy here, no need to test the _call function"""

    # Success
    def test_list_functions(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual('bar', r.result)

    def test_string_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc": "2.0", "method": "foo", "id": 1}')
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual('bar', r.result)

    # Errors
    def test_parse_error(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc')
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Parse error', r.json['error']['message'])

    def test_invalid_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', "id": 1})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Invalid request', r.json['error']['message'])

    def test_method_not_found(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'baz', 'id': 1})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Method not found', r.json['error']['message'])

    def test_invalid_params(self):
        def foo(x): # pylint: disable=unused-argument
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Invalid params', r.json['error']['message'])

    def test_explicitly_raised_exception(self):
        def foo():
            raise InvalidParams()
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Invalid params', r.json['error']['message'])

    def test_uncaught_exception(self):
        def foo():
            return 1/0
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertIsInstance(r, ErrorResponse)
        self.assertEqual('Server error', r.json['error']['message'])


class TestDispatchBatch(TestCase):

    # These are direct from the examples in the specification

    def invalid_json(self):
        def foo():
            return 'bar'
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32700, "message":
                "Parse error"}, "id": null},
            dispatch('[{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], \
                "id": "1"}, {"jsonrpc": "2.0", "method"]'))

    def empty_array(self):
        def foo():
            return 'bar'
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32600,
                "message": "Invalid Request"}, "id": null},
            dispatch([foo], []))

    def invalid_request(self):
        def foo():
            return 'bar'
        self.assertEqual(
            [{"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null}],
            dispatch([foo], [1]))

    def multiple_invalid_requests(self):
        def foo():
            return 'bar'
        self.assertEqual(
            [{"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null}],
            dispatch([foo], [1, 2, 3]))

    def mixed_requests_and_notifications(self):
        def foo():
            return 'bar'
        self.assertEqual(
            [{"jsonrpc": "2.0", "result": 7, "id": "1"},
            {"jsonrpc": "2.0", "result": 19, "id": "2"},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}, "id": null},
            {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": "5"},
            {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"}],
            dispatch([foo],
                [{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
                {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
                {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
                {"foo": "boo"},
                {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
                {"jsonrpc": "2.0", "method": "get_data", "id": "9"}]))

    def all_notifications(self):
        def foo():
            return 'bar'
        self.assertEqual(
            None,
            dispatch([foo],
                [{"jsonrpc": "2.0", "method": "notify_sum", "params": [1,2,4]},
                {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]}]))


if __name__ == '__main__':
    main()
