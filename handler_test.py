"""server_test.py"""
# pylint: disable=missing-docstring,line-too-long

from nose.tools import assert_equal # pylint: disable=no-name-in-module

from .handler import handle
from . import exceptions

class Handler: #pylint:disable=no-init,multiple-statements
    """Handler class for testing

    To test:
        method_only()
        one_param(string)
        two_param(one, two)
        many_args(*args)
        many_kwargs(**kwargs)
        positional_with_args(one, two, *args)
        positional_with_kwargs(one, two, **kwargs)
        positional_with_args_and_kwargs(one, two, **kwargs)
    """

    @staticmethod
    def method_only(): pass

    @staticmethod
    def one_positional(string): pass

    @staticmethod
    def two_positionals(one, two): pass

    @staticmethod
    def args(*args): pass

    @staticmethod
    def kwargs(**kwargs): pass

    @staticmethod
    def positionals_with_args(one, two, *args): pass

    @staticmethod
    def positionals_with_kwargs(one, two, **kwargs): pass

    @staticmethod
    def positionals_with_args_and_kwargs(one, two, *args, **kwargs): pass

    @staticmethod
    def add(number1, number2):
        """Add two numbers. Takes a list as args."""

        try:
            return number1 + number2

        except TypeError as e:
            raise exceptions.InvalidParams(str(e))

    @staticmethod
    def uppercase(*args):
        """Uppercase a string"""

        try:
            return args[0].upper()

        except KeyError:
            raise exceptions.InvalidParams()

    @staticmethod
    def lookup_surname(**kwargs):
        """Lookup a surname from a firstname"""

        try:
            if kwargs['firstname'] == 'John':
                return 'Smith'

        except KeyError:
            raise exceptions.InvalidParams()


# MethodNotFound

def test_MethodNotFound():

    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "go", "id": 1})
        raise AssertionError('MethodNotFound not raised')

    except exceptions.MethodNotFound as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": 1}', str(e))

# InvalidParams - this requires lots of testing because there are many ways the
# params can come through

# method_only

def test_method_only_ok():
    handle(Handler, {"jsonrpc": "2.0", "method": "method_only"})

def test_method_only_args():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "method_only", "params": [1], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() takes 0 positional arguments but 1 was given"}, "id": 1}', str(e))

def test_method_only_kwargs():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "method_only", "params": {"foo": "bar"}, "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

def test_method_only_both():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "method_only", "params": [1, 2, {"foo": "bar"}], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

# one_positional

def test_one_positional_ok():
    handle(Handler, {"jsonrpc": "2.0", "method": "one_positional", "params": [1]})

def test_one_positional_no_args():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "one_positional", "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() missing 1 required positional argument: \'string\'"}, "id": 1}', str(e))

def test_one_positional_two_args():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() takes 1 positional argument but 2 were given"}, "id": 1}', str(e))

def test_one_positional_kwargs():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "one_positional", "params": {"foo": "bar"}, "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

def test_one_positional_both():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2, {"foo": "bar"}], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

# two_positionals

def test_two_positionals_ok():
    handle(Handler, {"jsonrpc": "2.0", "method": "two_positionals", "params": [1, 2], "id": 1})

def test_two_positionals_no_args():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "two_positionals", "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() missing 2 required positional arguments: \'one\' and \'two\'"}, "id": 1}', str(e))

def test_two_positionals_one_arg():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "two_positionals", "params": [1], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() missing 1 required positional argument: \'two\'"}, "id": 1}', str(e))

def test_two_positionals_kwargs():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "two_positionals", "params": {"foo": "bar"}, "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

def test_two_positionals_both():
    try:
        handle(Handler, {"jsonrpc": "2.0", "method": "two_positionals", "params": [1, {"foo": "bar"}], "id": 1})
        raise AssertionError('InvalidParams not raised')

    except exceptions.InvalidParams as e:
        assert_equal('{"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1}', str(e))

# Test return results

def test_add_two_numbers():
    assert_equal(
        {'jsonrpc': '2.0', 'result': 3, 'id': 1},
        handle(Handler, {"jsonrpc": "2.0", "method": "add", "params": [1,2], "id": 1}
    ))

def test_uppercase():
    assert_equal(
        {'jsonrpc': '2.0', 'result': 'TEST', 'id': 1},
        handle(Handler, {"jsonrpc": "2.0", "method": "uppercase", "params": ["test"], "id": 1})
    )

def test_lookup_surname():
    assert_equal(
        {'jsonrpc': '2.0', 'result': 'Smith', 'id': 1},
        handle(Handler, {"jsonrpc": "2.0", "method": "lookup_surname", "params": {"firstname": "John"}, "id": 1})
    )
