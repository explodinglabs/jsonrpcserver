"""test_dispatcher.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods,no-init

from unittest import main
import json

from flask import Flask, request
from flask.ext.testing import TestCase #pylint:disable=import-error,no-name-in-module

from jsonrpcserver import bp, exceptions, dispatch, status

app = Flask(__name__)
app.register_blueprint(bp)

class HandleRequests:
    """Handling methods"""
    @staticmethod
    def get_5():
        return 5

def module_level_function():
    return 5

def method_only():
    pass

def one_positional(string):
    pass

def two_positionals(one, two):
    pass

def just_args(*args):
    pass

def just_kwargs(**kwargs):
    pass

def positionals_with_args(one, two, *args):
    pass

def positionals_with_kwargs(one, two, **kwargs):
    pass

def positionals_with_args_and_kwargs(one, two, *args, **kwargs):
    pass

def add(number1, number2):
    """Add two numbers. Takes a list as args."""
    try:
        return number1 + number2
    except TypeError as e:
        raise exceptions.InvalidParams(str(e))

def uppercase(*args):
    """Uppercase a string"""
    try:
        return args[0].upper()
    except KeyError as e:
        raise exceptions.InvalidParams(str(e))

def lookup_surname(**kwargs):
    """Lookup a surname from a firstname"""
    try:
        if kwargs['firstname'] == 'John':
            return 'Smith'
    except KeyError as e:
        raise exceptions.InvalidParams(str(e))


class TestDispatch(TestCase):
    """To test:
        method_only()
        one_param(string)
        two_param(one, two)
        many_args(*args)
        many_kwargs(**kwargs)
        positional_with_args(one, two, *args)
        positional_with_kwargs(one, two, **kwargs)
        positional_with_args_and_kwargs(one, two, *args, **kwargs)
    """

    @staticmethod
    def create_app():
        app.config['TESTING'] = True
        return app

    def assertJust200(self, response):
        self.assert200(response)
        self.assertEqual('', response.data.decode('utf-8'))

    def assertResultEquals(self, expected_result, response):
        self.assert200(response)
        self.assertEqual(expected_result, response.json['result'])

    def assertErrorEquals(self, expected_status, expected_message, response):
        self.assertStatus(expected_status, response)
        self.assertEqual(expected_error_message, response.json['error']['message'])

    # Misc

    def test_missing_jsonrpc_property(self):
        """jsonrpc is a required property"""
        with self.assertRaises(exceptions.InvalidRequest):
            dispatch({'jsonrp': '2.0', 'method': 'get'}),

    def test_method_not_found(self):
        with self.assertRaises(exceptions.MethodNotFound):
            dispatch({'jsonrpc': '2.0', 'method': 'get'}),

    def test_trying_to_call_magic_method(self):
        with self.assertRaises(exceptions.MethodNotFound):
            dispatch({'jsonrpc': '2.0', 'method': '__init__'}),

    def test_params_null(self):
        """Using 'params': null is not valid under the schema."""
        with self.assertRaises(exceptions.InvalidRequest):
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': None}),

    def test_id_null(self):
        """Using 'id': null *is* valid under the schema."""
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'id': None}),
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the params can come through

    # method_only

    def test_method_only_params_omitted(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only'})
        )

    def test_method_only_params_empty(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': []}),
        )

    def test_method_only_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1]})

    def test_method_only_two_args(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2]})

    def test_method_only_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': {'foo': 'bar'}})

    def test_method_only_both(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2, {'foo': 'bar'}]})

    # one_positional

    def test_one_positional_params_omitted(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional'}),

    def test_one_positional_one_arg(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1]})
        )

    def test_one_positional_two_args(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2]})

    def test_one_positional_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': {'foo': 'bar'}})

    def test_one_positional_both(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2, {'foo': 'bar'}]})

    # two_positionals

    def test_two_positionals_ok(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, 2]})
        )

    def test_two_positionals_params_omitted(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals'})

    def test_two_positionals_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1]})

    def test_two_positionals_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': {'foo': 'bar'}})

    def test_two_positionals_both(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, {'foo': 'bar'}]})
        )

    # just_args

    def test_just_args_ok(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, 2]})
        )

    def test_just_args_params_omitted(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args'})
        )

    def test_just_args_one_arg(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1]})
        )

    def test_just_args_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            response = dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': {'foo': 'bar'}})

    def test_just_args_both(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, {'foo': 'bar'}]})
        )

    # just_kwargs

    def test_just_kwargs_ok(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_just_kwargs_params_omitted(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs'})
        )

    def test_just_kwargs_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1]})

    def test_just_kwargs_kwargs(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_just_kwargs_both(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1, {'foo': 'bar'}]})

    # positionals_with_args

    def test_positionals_with_args_ok(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': ['foo', 42]})
        )

    def test_positionals_with_args_params_omitted(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args'})

    def test_positionals_with_args_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1]})

    def test_positionals_with_args_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': {'foo': 'bar'}})

    def test_positionals_with_args_both(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_kwargs

    def test_positionals_with_kwargs_ok(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})

    def test_positionals_with_kwargs_params_omitted(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs'})

    def test_positionals_with_kwargs_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1]})

    def test_positionals_with_kwargs_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': {'foo': 'bar'}})

    def test_positionals_with_kwargs_both(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_args_and_kwargs

    def test_positionals_with_args_and_kwargs_ok(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})
        )

    def test_positionals_with_args_and_kwargs_params_omitted(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs'})

    def test_positionals_with_args_and_kwargs_one_arg(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1]})

    def test_positionals_with_args_and_kwargs_kwargs(self):
        with self.assertRaises(exceptions.InvalidParams):
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': {'foo': 'bar'}})

    def test_positionals_with_args_and_kwargs_both(self):
        self.assertJust200(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # Test return results

    def test_add_two_numbers(self):
        self.assertResultEquals(
            3,
            dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [1, 2], 'id': 1})
        )

    def test_uppercase(self):
        self.assertResultEquals(
            'TEST',
            dispatch({'jsonrpc': '2.0', 'method': 'uppercase', 'params': ['test'], 'id': 1})
        )

    def test_lookup_surname(self):
        self.assertResultEquals(
            'Smith',
            dispatch({'jsonrpc': '2.0', 'method': 'lookup_surname', 'params': {'firstname': 'John'}, 'id': 1})
        )

    def test_passing_handling_object(self):
        self.assertResultEquals(
            5,
            dispatch({'jsonrpc': '2.0', 'method': 'get_5', 'id': 1}, HandleRequests)
        )

if __name__ == '__main__':
    main()
