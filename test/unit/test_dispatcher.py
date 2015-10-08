"""test_dispatcher.py"""
#pylint:disable=missing-docstring

from unittest import TestCase, main
import logging

from jsonrpcserver.dispatcher import _validate_arguments_against_signature, \
    _call
from jsonrpcserver.methods import Methods
from jsonrpcserver.dispatcher import dispatch
from jsonrpcserver.exceptions import InvalidParams


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
            _validate_arguments_against_signature(lambda x: None, None,
                {'foo': 'bar'})

    @staticmethod
    def test_keywords():
        _validate_arguments_against_signature(lambda **kwargs: None, None,
            {'foo': 'bar'})


class TestCall(TestCase):

    def test_list_of_functions(self):
        def foo():
            return 'bar'
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_list_of_lambdas(self):
        foo = lambda: 'bar'
        foo.__name__ = 'foo'
        self.assertEqual('bar', _call([foo], 'foo'))

    def test_methods(self):
        methods = Methods()
        methods.add(lambda: 1, 'one')
        self.assertEqual(1, _call(methods, 'one'))

    def test_methods_decorator(self):
        methods = Methods()
        @methods.add
        def one(): # pylint: disable=unused-variable
            return 1
        self.assertEqual(1, _call(methods, 'one'))

    def test_positionals(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        self.assertEqual(9, _call(methods, 'square', [3]))

    def test_positionals_and_keywords(self):
        def foo(*args, **kwargs):
            return 'bar'
        with self.assertRaises(InvalidParams):
            _call([foo], 'foo', [3], {'foo': 'bar'})


class TestDispatch(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_plain_list_of_functions(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)

    def test_plain_list_of_lambdas(self):
        foo = lambda: 'bar'
        foo.__name__ = 'foo'
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)

    def test_methods(self):
        methods = Methods()
        methods.add(lambda: 'bar', 'foo')
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        self.assertEqual('bar', r.result)

    def test_positional_args(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        self.assertEqual(9, dispatch(methods, {'jsonrpc': '2.0', 'method':
            'square', 'params': [3], 'id': 1}).result)

    def test_keyword_args(self):
        methods = Methods()
        @methods.add
        def upper(**kwargs): # pylint: disable=unused-variable
            return kwargs['word'].upper()
        r = dispatch(methods, {'jsonrpc': '2.0', 'method': 'upper', 'params':
            {'word': 'foo'}, 'id': 1})
        self.assertEqual('FOO', r.result)

    def test_string_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], '{"jsonrpc": "2.0", "method": "foo", "id": 1}')
        self.assertEqual('bar', r.result)

    # Errors
    def test_invalid_request(self):
        def foo():
            return 'bar'
        r = dispatch([foo], {'jsonrpc': '2.0'})
        self.assertEqual('Invalid request', r.json['error']['message'])
        self.assertEqual(400, r.http_status)

    def test_uncaught(self):
        def foo():
            return 1/0
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('Server error', r.json['error']['message'])

    def test_raise(self):
        def foo():
            raise InvalidParams()
        r = dispatch([foo], {'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('Invalid params', r.json['error']['message'])


if __name__ == '__main__':
    main()
