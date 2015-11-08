"""test_dispatcher.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main
from functools import partial
import logging

from jsonrpcserver.dispatcher import _validate_arguments_against_signature, \
    _call
from jsonrpcserver.methods import Methods
from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver.exceptions import InvalidParams
from jsonrpcserver import status
from jsonrpcserver.response import ErrorResponse, NotificationResponse, \
    RequestResponse


class TestValidateArgumentsAgainstSignature(TestCase):
    """Keep it simple here. No need to test the signature.bind function."""

    @staticmethod
    def test_no_arguments():
        _validate_arguments_against_signature(lambda: None, None, None)

    def test_no_arguments_too_many_positionals(self):
        with self.assertRaises(InvalidParams):
            _validate_arguments_against_signature(lambda: None, ['foo'], None)

    @staticmethod
    def test_positionals():
        _validate_arguments_against_signature(lambda x: None, [1], None)

    def test_positionals_not_passed(self):
        with self.assertRaises(InvalidParams):
            _validate_arguments_against_signature(
                lambda x: None, None, {'foo': 'bar'})

    @staticmethod
    def test_keywords():
        _validate_arguments_against_signature(
            lambda **kwargs: None, None, {'foo': 'bar'})


class TestCall(TestCase):

    def test_list_functions(self):
        def foo():
            return 'bar'
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_list_lambdas(self):
        foo = lambda: 'bar'
        foo.__name__ = 'foo'
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_list_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        double.__name__ = 'double'
        self.assertEqual(6, _call([double], 'double', [3]))

    def test_dict_functions(self):
        def foo():
            return 'bar'
        self.assertEqual('bar', _call({'baz': foo}, 'baz'))

    def test_dict_lambdas(self):
        self.assertEqual('bar', _call({'baz': lambda: 'bar'}, 'baz'))

    def test_dict_partials(self):
        multiply = lambda x, y: x * y
        self.assertEqual(6, _call({'baz': partial(multiply, 2)}, 'baz', [3]))

    def test_methods_functions(self):
        methods = Methods()
        def foo():
            return 'bar'
        methods.add_method(foo)
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_functions_with_decorator(self):
        methods = Methods()
        @methods.add_method
        def foo(): # pylint: disable=unused-variable
            return 'bar'
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_lambdas(self):
        methods = Methods()
        methods.add_method(lambda: 'bar', 'foo')
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        methods = Methods()
        methods.add_method(double, 'double')
        self.assertEqual(6, _call(methods, 'double', [3]))

    def test_positionals(self):
        methods = Methods()
        methods.add_method(lambda x: x * x, 'square')
        self.assertEqual(9, _call(methods, 'square', [3]))

    def test_keywords(self):
        def get_name(**kwargs):
            return kwargs['name']
        self.assertEqual('foo', _call([get_name], 'get_name', None,
                                      {'name': 'foo'}))

    def test_positionals_and_keywords(self):
        def foo(*args, **kwargs): # pylint: disable=unused-argument
            return 'bar'
        with self.assertRaises(InvalidParams):
            _call([foo], 'foo', [3], {'foo': 'bar'})


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
                "Parse error"}, "id": null}
            dispatch([{"jsonrpc": "2.0", "method": "sum", "params": [1,2,4],
                "id": "1"}, {"jsonrpc": "2.0", "method"],
        )

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
            dispatch([foo], [1])

    def multiple_invalid_requests(self):
        def foo():
            return 'bar'
        self.assertEqual([
            [{"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null},
            {"jsonrpc": "2.0", "error": {"code": -32600, "message":
                "Invalid Request"}, "id": null}],
            dispatch([foo], [1, 2, 3])

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
                {"jsonrpc": "2.0", "method": "get_data", "id": "9"}])

    def all_notifications(self):
        def foo():
            return 'bar'
        self.assertEqual(
            None,
            dispatch([foo],
                [{"jsonrpc": "2.0", "method": "notify_sum", "params": [1,2,4]},
                {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]}])


if __name__ == '__main__':
    main()
