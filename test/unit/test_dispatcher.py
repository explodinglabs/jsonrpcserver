"""test_dispatcher.py"""
#pylint:disable=missing-docstring,line-too-long

from unittest import TestCase, main

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
            _validate_arguments_against_signature(lambda x: None, None, {'foo': 'bar'})

    @staticmethod
    def test_keywords():
        _validate_arguments_against_signature(lambda **kwargs: None, None, {'foo': 'bar'})


class TestCall(TestCase):

    def test_plain_list_of_lambdas(self):
        one = lambda: 1
        one.__name__ = 'one'
        self.assertEqual(1, _call([one], 'one'))

    def test_methods_add(self):
        methods = Methods()
        methods.add(lambda: 1, 'one')
        self.assertEqual(1, _call(methods, 'one'))

    def test_methods_add_decorator(self):
        methods = Methods()
        @methods.add
        def one(): # pylint: disable=unused-variable
            return 1
        self.assertEqual(1, _call(methods, 'one'))

    def test_methods_add_with_args(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        self.assertEqual(9, _call(methods, 'square', [3]))


class TestDispatch(TestCase):

    def test_plain_list_of_functions(self):
        def one():
            return 1
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 1, 'id': 1}, 200),
            dispatch([one], {'jsonrpc': '2.0', 'method': 'one', 'id': 1})
        )

    def test_plain_list_of_lambdas(self):
        one = lambda: 1
        one.__name__ = 'one'
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 1, 'id': 1}, 200),
            dispatch([one], {'jsonrpc': '2.0', 'method': 'one', 'id': 1})
        )

    def test_methods_add(self):
        methods = Methods()
        methods.add(lambda: 1, 'one')
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 1, 'id': 1}, 200),
            dispatch(methods, {'jsonrpc': '2.0', 'method': 'one', 'id': 1})
        )

    def test_methods_add_with_args(self):
        methods = Methods()
        methods.add(lambda x: x * x, 'square')
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 9, 'id': 1}, 200),
            dispatch(methods, {'jsonrpc': '2.0', 'method': 'square', 'params': [3], 'id': 1})
        )

    def test_methods_add_with_kwargs(self):
        methods = Methods()
        @methods.add
        def upper(**kwargs): # pylint: disable=unused-variable
            return kwargs['word'].upper()
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 'FOO', 'id': 1}, 200),
            dispatch(methods, {'jsonrpc': '2.0', 'method': 'upper', 'params': {'word': 'foo'}, 'id': 1})
        )

    def test_methods_add_with_invalid_params(self):
        methods = Methods()
        methods.add(lambda: None, 'foo')
        self.assertEqual(
            ({'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}, 400),
            dispatch(methods, {'jsonrpc': '2.0', 'method': 'foo', 'params': [1], 'id': 1})
        )

    def test_string_request(self):
        def one():
            return 1
        self.assertEqual(
            ({'jsonrpc': '2.0', 'result': 1, 'id': 1}, 200),
            dispatch([one], '{"jsonrpc": "2.0", "method": "one", "id": 1}')
        )

if __name__ == '__main__':
    main()
