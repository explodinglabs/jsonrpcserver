"""test_request.py"""
# pylint: disable=missing-docstring,line-too-long,blacklisted-name

from unittest import TestCase, main
import logging

from functools import partial

from jsonrpcserver.request import _convert_camel_case, \
    _convert_camel_case_keys, _validate_arguments_against_signature, _call, \
    _get_arguments, Request
from jsonrpcserver.response import ErrorResponse, RequestResponse, \
    NotificationResponse
from jsonrpcserver.exceptions import InvalidRequest, InvalidParams
from jsonrpcserver.methods import Methods
from jsonrpcserver import status


def foo():
    return 'bar'


class TestConvertCamelCase(TestCase):

    def test(self):
        self.assertEqual('foo_bar', _convert_camel_case('fooBar'))


class TestConvertCamelCaseKeys(TestCase):

    def test(self):
        d = {'fooKey': 1, 'aDict': {'fooKey': 1, 'barKey': 2}}
        self.assertEqual({'foo_key': 1, 'a_dict': {'foo_key': 1, 'bar_key': 2}}, \
                _convert_camel_case_keys(d))


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
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_list_lambdas(self):
        foo = lambda: 'bar' # pylint: disable=redefined-outer-name
        foo.__name__ = 'foo'
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_list_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        double.__name__ = 'double'
        self.assertEqual(6, _call([double], 'double', [3]))

    def test_dict_functions(self):
        self.assertEqual('bar', _call({'baz': foo}, 'baz'))

    def test_dict_lambdas(self):
        self.assertEqual('bar', _call({'baz': lambda: 'bar'}, 'baz'))

    def test_dict_partials(self):
        multiply = lambda x, y: x * y
        self.assertEqual(6, _call({'baz': partial(multiply, 2)}, 'baz', [3]))

    def test_methods_functions(self):
        methods = Methods()
        methods.add_method(foo)
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_functions_with_decorator(self):
        methods = Methods()
        @methods.add_method
        def foo(): # pylint: disable=redefined-outer-name,unused-variable
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
        def foo(*args, **kwargs): # pylint: disable=redefined-outer-name,unused-argument
            return 'bar'
        with self.assertRaises(InvalidParams):
            _call([foo], 'foo', [3], {'foo': 'bar'})


class TestGetArguments(TestCase):

    def test_none(self):
        self.assertEqual((None, None), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo'}))

    def test_positional(self):
        self.assertEqual(([2, 3], None), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo', 'params': [2, 3]}))

    def test_keyword(self):
        self.assertEqual((None, {'foo': 'bar'}), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo', 'params': {'foo': 'bar'}}))

    def test_invalid_none(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': None})

    def test_invalid_numeric(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': 5})

    def test_invalid_string(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': 'str'})


class TestRequestInit(TestCase):

    def test_invalid_request(self):
        with self.assertRaises(InvalidRequest):
            Request({'jsonrpc': '2.0'})

    def test_ok(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('foo', r.method_name)

    def test_positional_args(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'params': [2, 3]})
        self.assertEqual([2, 3], r.args)

    def test_keyword_args(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'params': {'foo': 'bar'}})
        self.assertEqual({'foo': 'bar'}, r.kwargs)

    def test_request_id(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 99})
        self.assertEqual(99, r.request_id)

    def test_request_id_notification(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual(None, r.request_id)

    def test_convert_camel_case(self):
        Request.convert_camel_case = True
        r = Request({'jsonrpc': '2.0', 'method': 'fooMethod', 'params': {
            'fooParam': 1, 'aDict': {'barParam': 1}}})
        self.assertEqual('foo_method', r.method_name)
        self.assertEqual({'foo_param': 1, 'a_dict': {'bar_param': 1}}, r.kwargs)
        Request.convert_camel_case = False


class TestRequestIsNotification(TestCase):

    def test_true(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertTrue(r.is_notification)

    def test_false(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 99})
        self.assertFalse(r.is_notification)


class TestRequestProcessNotifications(TestCase):
    """Go easy here, no need to test the _call function"""

    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Success
    def test_success(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'}).process([foo])
        self.assertIsInstance(r, NotificationResponse)

    def test_method_not_found(self):
        r = Request({'jsonrpc': '2.0', 'method': 'baz'}).process([foo])
        self.assertIsInstance(r, NotificationResponse)

    def test_invalid_params(self):
        def foo(x): # pylint: disable=redefined-outer-name,unused-argument
            return 'bar'
        r = Request({'jsonrpc': '2.0', 'method': 'foo'}).process([foo])
        self.assertIsInstance(r, NotificationResponse)

    def test_explicitly_raised_exception(self):
        def foo(): # pylint: disable=redefined-outer-name
            raise InvalidParams()
        r = Request({'jsonrpc': '2.0', 'method': 'foo'}).process([foo])
        self.assertIsInstance(r, NotificationResponse)

    def test_uncaught_exception(self):
        def foo(): # pylint: disable=redefined-outer-name
            return 1/0
        r = Request({'jsonrpc': '2.0', 'method': 'foo'}).process([foo])
        self.assertIsInstance(r, NotificationResponse)

    # Configuration
    def test_config_notification_errors_on(self):
        # Should return "method not found" error
        request = Request({'jsonrpc': '2.0', 'method': 'baz'})
        request.notification_errors = True
        r = request.process([foo])
        self.assertIsInstance(r, ErrorResponse)

    def test_configuring_http_status(self):
        NotificationResponse.http_status = status.HTTP_OK
        r = Request({'jsonrpc': '2.0', 'method': 'foo'}).process([foo])
        self.assertEqual(status.HTTP_OK, r.http_status)
        NotificationResponse.http_status = status.HTTP_NO_CONTENT


class TestRequestProcessRequests(TestCase):
    """Go easy here, no need to test the _call function"""

    # Success
    def test(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 1}).process([foo])
        self.assertIsInstance(r, RequestResponse)
        self.assertEqual('bar', r['result'])


if __name__ == '__main__':
    main()
