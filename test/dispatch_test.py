"""dispatch_test.py"""
# pylint:disable=missing-docstring,line-too-long,no-init,multiple-statements,too-many-public-methods,no-self-use,no-member

import json

from flask import Flask
from flask.ext.testing import TestCase #pylint:disable=import-error,no-name-in-module

from jsonrpcserver import bp, exceptions, dispatch, status

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/', methods=['POST'])
def index():
    return dispatch(HandleRequests)


class HandleRequests:
    """Handling methods"""
    #pylint:disable=unused-argument

    @staticmethod
    def method_only():
        pass

    @staticmethod
    def one_positional(string):
        pass

    @staticmethod
    def two_positionals(one, two):
        pass

    @staticmethod
    def just_args(*args):
        pass

    @staticmethod
    def just_kwargs(**kwargs):
        pass

    @staticmethod
    def positionals_with_args(one, two, *args):
        pass

    @staticmethod
    def positionals_with_kwargs(one, two, **kwargs):
        pass

    @staticmethod
    def positionals_with_args_and_kwargs(one, two, *args, **kwargs):
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

        except KeyError as e:
            raise exceptions.InvalidParams(str(e))

    @staticmethod
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

    def create_app(self):

        app.config['TESTING'] = True
        return app

    def post_request(self, request_str):

        return self.client.post(
            '/', headers={'content-type': 'application/json'}, \
            data=json.dumps(request_str)) #pylint:disable=maybe-no-member

    def post(self, expected_http_status_code, expected_response_dict, request_str):

        response = self.post_request(request_str)

        if expected_response_dict:
            self.assertEqual(expected_response_dict, response.json)
        else:
            self.assertEqual('', response.data.decode('utf-8'))

        self.assertEqual(expected_http_status_code, response.status_code)

    # InvalidRequest
    def test_InvalidRequest(self):
        self.post(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_REQUEST_CODE, 'message': 'Invalid request', 'data': "'jsonrpc' is a required property"}, 'id': None},
            {'jsonrp': '2.0', 'method': 'get'},
        )

    # MethodNotFound

    def test_MethodNotFound(self):
        self.post(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_METHOD_NOT_FOUND_CODE, 'message': 'Method not found', 'data': 'get'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'get', 'id': 1},
        )

    def test_trying_to_call_magic_method(self):
        self.post(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_METHOD_NOT_FOUND_CODE, 'message': 'Method not found', 'data': '__init__'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': '__init__', 'id': 1},
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the params can come through

    # method_only

    def test_method_only_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'method_only'}
        )

    def test_method_only_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'method_only() takes 0 positional arguments but 1 was given'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': [1], 'id': 1}
        )

    def test_method_only_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'method_only() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': {'foo': 'bar'}, 'id': 1}
        )

    def test_method_only_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'method_only() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2, {'foo': 'bar'}], 'id': 1}
        )

    # one_positional

    def test_one_positional_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1]}
        )

    def test_one_positional_no_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'one_positional() missing 1 required positional argument: \'string\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'one_positional', 'id': 1},
        )

    def test_one_positional_two_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'one_positional() takes 1 positional argument but 2 were given'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2], 'id': 1},
        )

    def test_one_positional_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'one_positional() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_one_positional_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'one_positional() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2, {'foo': 'bar'}], 'id': 1},
        )

    # two_positionals

    def test_two_positionals_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, 2], 'id': 1}
        )

    def test_two_positionals_no_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'two_positionals() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'id': 1},
        )

    def test_two_positionals_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'two_positionals() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1], 'id': 1},
        )

    def test_two_positionals_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'two_positionals() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_two_positionals_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'two_positionals() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # just_args

    def test_just_args_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, 2], 'id': 1}
        )

    def test_just_args_no_args(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_args', 'id': 1},
        )

    def test_just_args_one_arg(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1], 'id': 1},
        )

    def test_just_args_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'just_args() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_just_args_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'just_args() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # just_kwargs

    def test_just_kwargs_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}, 'id': 1}
        )

    def test_just_kwargs_no_args(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'id': 1},
        )

    def test_just_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'just_kwargs() takes 0 positional arguments but 1 was given'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1], 'id': 1},
        )

    def test_just_kwargs_kwargs(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_just_kwargs_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'just_kwargs() takes 0 positional arguments but 1 was given'}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # positionals_with_args

    def test_positionals_with_args_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': ['foo', 42], 'id': 1}
        )

    def test_positionals_with_args_no_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'id': 1},
        )

    def test_positionals_with_args_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1], 'id': 1},
        )

    def test_positionals_with_args_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_positionals_with_args_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args() got an unexpected keyword argument \'foo\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # positionals_with_kwargs

    def test_positionals_with_kwargs_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': ['foo', 42, {'foo': 'bar'}], 'id': 1}
        )

    def test_positionals_with_kwargs_no_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_kwargs() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'id': 1},
        )

    def test_positionals_with_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_kwargs() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1], 'id': 1},
        )

    def test_positionals_with_kwargs_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_kwargs() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_positionals_with_kwargs_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_kwargs() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # positionals_with_args_and_kwargs

    def test_positionals_with_args_and_kwargs_ok(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': None, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': ['foo', 42, {'foo': 'bar'}], 'id': 1}
        )

    def test_positionals_with_args_and_kwargs_no_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args_and_kwargs() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'id': 1},
        )

    def test_positionals_with_args_and_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args_and_kwargs() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1], 'id': 1},
        )

    def test_positionals_with_args_and_kwargs_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args_and_kwargs() missing 2 required positional arguments: \'one\' and \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': {'foo': 'bar'}, 'id': 1},
        )

    def test_positionals_with_args_and_kwargs_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            {'jsonrpc': '2.0', 'error': {'code': status.JSONRPC_INVALID_PARAMS_CODE, 'message': status.JSONRPC_INVALID_PARAMS_TEXT, 'data': 'positionals_with_args_and_kwargs() missing 1 required positional argument: \'two\''}, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1, {'foo': 'bar'}], 'id': 1},
        )

    # Test return results

    def test_add_two_numbers(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': 3, 'id': 1},
            {'jsonrpc': '2.0', 'method': 'add', 'params': [1, 2], 'id': 1}
        )

    def test_uppercase(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': 'TEST', 'id': 1},
            {'jsonrpc': '2.0', 'method': 'uppercase', 'params': ['test'], 'id': 1}
        )

    def test_lookup_surname(self):
        self.post(
            status.HTTP_200_OK,
            {'jsonrpc': '2.0', 'result': 'Smith', 'id': 1},
            {'jsonrpc': '2.0', 'method': 'lookup_surname', 'params': {'firstname': 'John'}, 'id': 1}
        )
