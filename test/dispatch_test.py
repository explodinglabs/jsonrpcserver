"""dispatch_test.py"""
# pylint:disable=missing-docstring,line-too-long,no-init,multiple-statements,too-many-public-methods,no-self-use,no-member

import sys
import json

from flask import Flask
from flask.ext.testing import TestCase #pylint:disable=import-error,no-name-in-module

from jsonrpcserver import bp
from jsonrpcserver import exceptions
from jsonrpcserver import dispatch

HTTP_STATUS_BAD_REQUEST = 400

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/', methods=['POST'])
def index():
    return dispatch(sys.modules[__name__])


# RPC Method handlers

def method_only():
    pass

def one_positional(string): #pylint:disable=unused-argument
    pass

def two_positionals(one, two): #pylint:disable=unused-argument
    pass

def just_args(*args): #pylint:disable=unused-argument
    pass

def just_kwargs(**kwargs): #pylint:disable=unused-argument
    pass

def positionals_with_args(one, two, *args): #pylint:disable=unused-argument
    pass

def positionals_with_kwargs(one, two, **kwargs): #pylint:disable=unused-argument
    pass

def positionals_with_args_and_kwargs(one, two, *args, **kwargs): #pylint:disable=unused-argument
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

    except KeyError:
        raise exceptions.InvalidParams()

def lookup_surname(**kwargs):
    """Lookup a surname from a firstname"""

    try:
        if kwargs['firstname'] == 'John':
            return 'Smith'

    except KeyError:
        raise exceptions.InvalidParams()


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

    def create_app(self):

        app.config['TESTING'] = True
        return app

    def post_request(self, request_str):
        return self.client.post(
            '/', headers={'content-type': 'application/json'}, \
            data=json.dumps(request_str)) #pylint:disable=maybe-no-member

    def post(self, expected_response_dict, request_str, expected_status_code=200):

        response = self.post_request(request_str)

        self.assertEqual(expected_status_code, response.status_code)

        if expected_response_dict:
            self.assertEqual(expected_response_dict, response.json)
        else:
            self.assertEqual("", response.data.decode('utf-8'))

    # MethodNotFound
    def test_MethodNotFound(self):
        self.post(
            {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'unknown', 'id': 1},
            HTTP_STATUS_BAD_REQUEST
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
            {"jsonrpc": "2.0", "method": "method_only", "params": [1], "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_method_only_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "method_only", "params": {"foo": "bar"}, "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_method_only_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "method_only() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "method_only", "params": [1, 2, {"foo": "bar"}], "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    # one_positional

    def test_one_positional_ok(self):
        self.post(
            '',
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1]}
        )

    def test_one_positional_no_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() missing 1 required positional argument: \'string\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_one_positional_two_args(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() takes 1 positional argument but 2 were given"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2], "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_one_positional_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": {"foo": "bar"}, "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_one_positional_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "one_positional() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "one_positional", "params": [1, 2, {"foo": "bar"}], "id": 1},
            HTTP_STATUS_BAD_REQUEST
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
            {"jsonrpc": "2.0", "method": "two_positionals", "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_two_positionals_one_arg(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() missing 1 required positional argument: \'two\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": [1], "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_two_positionals_kwargs(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": {"foo": "bar"}, "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    def test_two_positionals_both(self):
        self.post(
            {"jsonrpc": "2.0", "error": {"code": -32602, "message": "two_positionals() got an unexpected keyword argument \'foo\'"}, "id": 1},
            {"jsonrpc": "2.0", "method": "two_positionals", "params": [1, {"foo": "bar"}], "id": 1},
            HTTP_STATUS_BAD_REQUEST
        )

    # Test return results

    def test_add_two_numbers(self):
        self.post(
            {'jsonrpc': '2.0', 'result': 3, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'add', 'params': [1, 2], 'id': 1}
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
