"""test_dispatcher.py"""
#pylint:disable=missing-docstring

from unittest import TestCase, main
from functools import partial
import logging

from jsonrpcserver.dispatcher import _validate_arguments_against_signature, \
    _call
from jsonrpcserver.methods import Methods
from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver.exceptions import InvalidParams
from jsonrpcserver import status


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
        methods.add(foo)
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_functions_with_decorator(self):
        methods = Methods()
        @methods.add
        def foo(): # pylint: disable=unused-variable
            return 'bar'
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_lambdas(self):
        methods = Methods()
        methods.add(lambda: 'bar', 'foo')
        self.assertEqual('bar', _call(methods, 'foo'))

    def test_methods_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        methods = Methods()
        methods.add(double, 'double')
        self.assertEqual(6, _call(methods, 'double', [3]))

    def test_positionals(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        self.assertEqual(9, _call(methods, 'square', [3]))

    def test_positionals_and_keywords(self):
        def foo(*args, **kwargs): # pylint: disable=unused-argument
            return 'bar'
        with self.assertRaises(InvalidParams):
            _call([foo], 'foo', [3], {'foo': 'bar'})


class TestDispatch(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    # Success
    def test_list_functions(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_list_lambdas(self):
        foo = lambda: 'bar'
        foo.__name__ = 'foo'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_list_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        double.__name__ = 'double'
        r = dispatch([double], {'jsonrpc': '2.0', 'method': 'double',
                                'params': [3], 'id': 1})
        self.assertEqual(6, r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_dict_functions(self):
        def foo():
            return 'bar'
        r = dispatch({'baz': foo}, {'jsonrpc': '2.0', 'method': 'baz', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_dict_lambdas(self):
        foo = lambda: 'bar'
        r = dispatch({'baz': foo}, {'jsonrpc': '2.0', 'method': 'baz', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_dict_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        r = dispatch({'dbl': double}, {'jsonrpc': '2.0', 'method': 'dbl',
                                       'params': [3], 'id': 1})
        self.assertEqual(6, r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_methods_functions(self):
        def foo():
            return 'bar'
        methods = Methods()
        methods.add(foo)
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_methods_lambdas(self):
        methods = Methods()
        methods.add(lambda: 'bar', 'foo')
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_methods_partials(self):
        multiply = lambda x, y: x * y
        double = partial(multiply, 2)
        double.__name__ = 'double'
        methods = Methods()
        methods.add(double, 'double')
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'double', 'params':
                               [3], 'id': 1})
        self.assertEqual(6, r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_positional_args(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'square', 'params':
                               [3], 'id': 1})
        self.assertEqual(9, r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_keyword_args(self):
        methods = Methods()
        @methods.add
        def upper(**kwargs): # pylint: disable=unused-variable
            return kwargs['word'].upper()
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'upper', 'params':
                               {'word': 'foo'}, 'id': 1})
        self.assertEqual('FOO', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_string_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc": "2.0", "method": "foo", "id": 1}')
        self.assertEqual('bar', r.result)
        self.assertEqual(status.HTTP_OK, r.http_status)

    def test_notification(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual(None, r.result)
        self.assertEqual(None, r.json)
        self.assertEqual('', r.body)
        self.assertEqual(status.HTTP_NO_CONTENT, r.http_status)

    # Errors
    def test_parse_error(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc')
        self.assertEqual('Parse error', r.json['error']['message'])
        self.assertEqual(status.HTTP_BAD_REQUEST, r.http_status)

    def test_invalid_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0'})
        self.assertEqual('Invalid request', r.json['error']['message'])
        self.assertEqual(status.HTTP_BAD_REQUEST, r.http_status)

    def test_method_not_found(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'baz'})
        self.assertEqual('Method not found', r.json['error']['message'])
        self.assertEqual(status.HTTP_NOT_FOUND, r.http_status)

    def test_invalid_params(self):
        def foo(x): # pylint: disable=unused-argument
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('Invalid params', r.json['error']['message'])
        self.assertEqual(status.HTTP_BAD_REQUEST, r.http_status)

    def test_server_error(self):
        def foo():
            return 1/0
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('Server error', r.json['error']['message'])
        self.assertEqual(status.HTTP_INTERNAL_ERROR, r.http_status)

    def test_explicitly_raised_exception(self):
        def foo():
            raise InvalidParams()
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('Invalid params', r.json['error']['message'])
        self.assertEqual(status.HTTP_BAD_REQUEST, r.http_status)


if __name__ == '__main__':
    main()
