"""test_dispatcher.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods,no-init

from unittest import main
import json

from flask import Flask, request
from flask.ext.testing import TestCase #pylint:disable=import-error,no-name-in-module

from jsonrpcserver import bp, exceptions, dispatch, status

app = Flask(__name__)
app.register_blueprint(bp)

@app.route('/', methods=['POST'])
def index():
    return dispatch(request.get_json(), HandleRequests)


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

    @staticmethod
    def create_app():
        app.config['TESTING'] = True
        return app

    def post_request(self, request_str):
        return self.client.post(
            '/', headers={'content-type': 'application/json'}, \
            data=json.dumps(request_str)) #pylint:disable=maybe-no-member

    def post(self, expected_http_status_code, expected_response_text, request_str):

        response = self.post_request(request_str)

        self.assertEqual(expected_http_status_code, response.status_code)

        if expected_response_text:
            if expected_http_status_code == 200:
                self.assertEqual(expected_response_text, response.json['result'])
            else:
                self.assertEqual(expected_response_text, response.json['error']['message'])
        else:
            self.assertEqual('', response.data.decode('utf-8'))

    # Misc

    def test_missing_jsonrpc_property(self):
        """jsonrpc is a required property"""
        self.post(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT,
            {'jsonrp': '2.0', 'method': 'get'},
        )

    def test_method_not_found(self):
        self.post(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            'Method not found',
            {'jsonrpc': '2.0', 'method': 'get'},
        )

    def test_trying_to_call_magic_method(self):
        self.post(
            status.JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            'Method not found',
            {'jsonrpc': '2.0', 'method': '__init__'},
        )

    def test_params_null(self):
        """Using 'params': null is not valid under the schema."""
        self.post(
            status.JSONRPC_INVALID_REQUEST_HTTP_CODE,
            status.JSONRPC_INVALID_REQUEST_TEXT,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': None},
        )

    def test_id_null(self):
        """Using 'id': null *is* valid under the schema."""
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'method_only', 'id': None},
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the params can come through

    # method_only

    def test_method_only_params_omitted(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'method_only'}
        )

    def test_method_only_params_empty(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': []},
        )

    def test_method_only_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': [1]}
        )

    def test_method_only_two_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2]}
        )

    def test_method_only_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': {'foo': 'bar'}}
        )

    def test_method_only_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2, {'foo': 'bar'}]}
        )

    # one_positional

    def test_one_positional_params_omitted(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'one_positional'},
        )

    def test_one_positional_one_arg(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1]}
        )

    def test_one_positional_two_args(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2]},
        )

    def test_one_positional_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': {'foo': 'bar'}},
        )

    def test_one_positional_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2, {'foo': 'bar'}]},
        )

    # two_positionals

    def test_two_positionals_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, 2]}
        )

    def test_two_positionals_params_omitted(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'two_positionals'},
        )

    def test_two_positionals_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1]},
        )

    def test_two_positionals_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': {'foo': 'bar'}},
        )

    def test_two_positionals_both(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, {'foo': 'bar'}]},
        )

    # just_args

    def test_just_args_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, 2]}
        )

    def test_just_args_params_omitted(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_args'},
        )

    def test_just_args_one_arg(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1]},
        )

    def test_just_args_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': {'foo': 'bar'}},
        )

    def test_just_args_both(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, {'foo': 'bar'}]},
        )

    # just_kwargs

    def test_just_kwargs_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}}
        )

    def test_just_kwargs_params_omitted(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_kwargs'},
        )

    def test_just_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1]},
        )

    def test_just_kwargs_kwargs(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}},
        )

    def test_just_kwargs_both(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1, {'foo': 'bar'}]},
        )

    # positionals_with_args

    def test_positionals_with_args_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': ['foo', 42]}
        )

    def test_positionals_with_args_params_omitted(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args'},
        )

    def test_positionals_with_args_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1]},
        )

    def test_positionals_with_args_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': {'foo': 'bar'}},
        )

    def test_positionals_with_args_both(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1, {'foo': 'bar'}]},
        )

    # positionals_with_kwargs

    def test_positionals_with_kwargs_ok(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]}
        )

    def test_positionals_with_kwargs_params_omitted(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs'},
        )

    def test_positionals_with_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1]},
        )

    def test_positionals_with_kwargs_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': {'foo': 'bar'}},
        )

    def test_positionals_with_kwargs_both(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1, {'foo': 'bar'}]},
        )

    # positionals_with_args_and_kwargs

    def test_positionals_with_args_and_kwargs_ok(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]}
        )

    def test_positionals_with_args_and_kwargs_params_omitted(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs'},
        )

    def test_positionals_with_args_and_kwargs_one_arg(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1]},
        )

    def test_positionals_with_args_and_kwargs_kwargs(self):
        self.post(
            status.JSONRPC_INVALID_PARAMS_HTTP_CODE,
            status.JSONRPC_INVALID_PARAMS_TEXT,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': {'foo': 'bar'}},
        )

    def test_positionals_with_args_and_kwargs_both(self):
        self.post(
            status.HTTP_200_OK,
            None,
            {'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1, {'foo': 'bar'}]},
        )

    # Test return results

    def test_add_two_numbers(self):
        self.post(
            status.HTTP_200_OK,
            3,
            {'jsonrpc': '2.0', 'method': 'add', 'params': [1, 2], 'id': 1}
        )

    def test_uppercase(self):
        self.post(
            status.HTTP_200_OK,
            'TEST',
            {'jsonrpc': '2.0', 'method': 'uppercase', 'params': ['test'], 'id': 1}
        )

    def test_lookup_surname(self):
        self.post(
            status.HTTP_200_OK,
            'Smith',
            {'jsonrpc': '2.0', 'method': 'lookup_surname', 'params': {'firstname': 'John'}, 'id': 1}
        )

if __name__ == '__main__':
    main()
