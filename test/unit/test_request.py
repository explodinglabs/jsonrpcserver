"""test_request.py"""
# pylint: disable=missing-docstring,line-too-long

from unittest import TestCase, main

from functools import partial

from jsonrpcserver.request import Request, _get_arguments, \
    _validate_arguments_against_signature, _call
from jsonrpcserver.exceptions import ParseError, InvalidRequest, InvalidParams
from jsonrpcserver.methods import Methods


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
        with self.assertRaises(KeyError):
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


class TestRequestIsNotification(TestCase):

    def test_true(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertTrue(r.is_notification)

    def test_false(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 99})
        self.assertFalse(r.is_notification)


if __name__ == '__main__':
    main()
