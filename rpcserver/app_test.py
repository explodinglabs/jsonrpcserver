"""server_test.py"""
# pylint: disable=missing-docstring,line-too-long

from nose.tools import assert_equal # pylint: disable=no-name-in-module
import unittest
import json

from .app import App
from . import exceptions

class DummyApp(App): #pylint:disable=too-many-public-methods

    def method_only(self):
        pass

    def one_positional(self, string):
        pass

    def two_positionals(self, one, two):
        pass

    def args(self, *args):
        pass

    def kwargs(self, **kwargs):
        pass

    def positionals_with_args(self, one, two, *args):
        pass

    def positionals_with_kwargs(self, one, two, **kwargs):
        pass

    def positionals_with_args_and_kwargs(self, one, two, *args, **kwargs):
        pass

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

testapp = DummyApp(__name__)

class AppTestCase(unittest.TestCase): #pylint:disable=no-init,multiple-statements,too-many-public-methods
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

    def setUp(self):
        testapp.config['TESTING'] = True
        self.app = testapp.test_client()

    def post(self, expected_response, request):

        response = self.app.post(
            '/', headers={'content-type': 'application/json'}, \
            data=json.dumps(request)).data.decode('utf-8') #pylint:disable=maybe-no-member

        if response:
            response = json.loads(response)

        assert_equal(
            expected_response,
            response
        )

    # MethodNotFound
    def test_MethodNotFound(self):
        self.post(
            {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'unknown', 'id': 1}
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the st params can come through

    # method_only

    def test_method_only_ok(self):
        self.post(
            None,
            {"jsonrpc": "2.0", "method": "method_only"}
        )

    def test_method_only_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() takes 0 positional arguments but 1 was given"}, "id": 1},
            {"jsonrpc": "2.0", "method": "method_only", "params": [1], "id": 1}
        )

    def test_method_only_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "method_only", "params": {"foo": "bar"}, "id": 1}
        )

    def test_method_only_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "method_only", "params": [1, 2, {"foo": "bar"}], "id": 1}
        )

    # one_positional

    def test_one_positional_ok(self):
        self.post(
            None,
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1]}
        )

    def test_one_positional_no_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() missing 1 required positional argument: \'string\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "id": 1}
        )

    def test_one_positional_two_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() takes 1 positional argument but 2 were given"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2], "id": 1}
        )

    def test_one_positional_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": {"foo": "bar"}, "id": 1},
        )

    def test_one_positional_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2, {"foo": "bar"}], "id": 1}
        )

    # two_positionals

    def test_two_positionals_ok(self):
        self.post(
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": [1, 2], "id": 1}
        )

    def test_two_positionals_no_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() missing 2 required positional arguments: \'one\' and \'two\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "id": 1}
        )

    def test_two_positionals_one_arg(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() missing 1 required positional argument: \'two\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": [1], "id": 1}
        )

    def test_two_positionals_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": {"foo": "bar"}, "id": 1}
        )

    def test_two_positionals_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": [1, {"foo": "bar"}], "id": 1}
        )

    # Test return results

    def test_add_two_numbers(self):
        self.post(
            {'jsonrpc': '2.0', 'result': 3, 'id': 1},
            {"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1}
        )

    def test_uppercase(self):
        self.post(
            {'jsonrpc': '2.0', 'result': 'TEST', 'id': 1},
            {"jsonrpc": "2.0", "method": "uppercase", "params": ["test"], "id": 1}
        )

    def test_lookup_surname(self):
        self.post(
            {'jsonrpc': '2.0', 'result': 'Smith', 'id': 1},
            {"jsonrpc": "2.0", "method": "lookup_surname", "params": {"firstname": "John"}, "id": 1}
        )
