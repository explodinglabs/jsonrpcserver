"""test_dispatcher.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods,no-init,unused-argument

from unittest import TestCase, main, skip, expectedFailure

from jsonrpcserver.dispatcher import jsonrpc_method, dispatch
from jsonrpcserver.exceptions import ServerError
from jsonrpcserver.status import JSONRPC_INVALID_PARAMS_TEXT, \
    JSONRPC_INVALID_PARAMS_HTTP_CODE, JSONRPC_METHOD_NOT_FOUND_HTTP_CODE, \
    JSONRPC_METHOD_NOT_FOUND_TEXT, JSONRPC_INVALID_REQUEST_TEXT, \
    JSONRPC_INVALID_REQUEST_HTTP_CODE, JSONRPC_SERVER_ERROR_HTTP_CODE, \
    JSONRPC_SERVER_ERROR_TEXT


jsonrpc_method(lambda : None, 'method_only')
jsonrpc_method(lambda string: None, 'one_positional')
jsonrpc_method(lambda one, two: None, 'two_positionals')
jsonrpc_method(lambda *args: None, 'just_args')
jsonrpc_method(lambda **kwargs: None, 'just_kwargs')
jsonrpc_method(lambda one, two, *args: None, 'positionals_with_args')
jsonrpc_method(lambda one, two, **kwargs: None, 'positionals_with_kwargs')
jsonrpc_method(lambda one, two, *args, **kwargs: None, 'positionals_with_args_and_kwargs')
jsonrpc_method(lambda one, two: one + two, 'add')
jsonrpc_method(lambda string: string.upper(), 'uppercase')

@jsonrpc_method
def lookup_surname(**kwargs):
    """Test using a full function, not a lambda"""
    if kwargs['firstname'] == 'John':
        return 'Smith'

class HandleRequests:
    """Test using a class method, not a function"""
    @staticmethod
    @jsonrpc_method
    def get_5():
        return 5

@jsonrpc_method
def raise_jsonrpcservererror():
    raise ServerError('Database error', 'Column "Insecure" does not exist')

@jsonrpc_method
def raise_other_error():
    raise ValueError('Value too low')


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

    def assertNoContent(self, response):
        result, status = response
        self.assertEqual(204, status)
        self.assertEqual(None, result)

    def assertErrorEquals(self, expected_status, expected_result, response):
        result, status = response
        self.assertEqual(expected_status, status)
        self.assertEqual(expected_result, result['error']['message'])

    def assertResultEquals(self, expected_result, response):
        result, status = response
        self.assertEqual(200, status)
        self.assertEqual(expected_result, result['result'])

    # InvalidRequest

    def test_missing_jsonrpc_property(self):
        """jsonrpc is a required property"""
        self.assertErrorEquals(
            JSONRPC_INVALID_REQUEST_HTTP_CODE,
            JSONRPC_INVALID_REQUEST_TEXT,
            dispatch({'jsonrp': '2.0', 'method': 'get'})
        )

    def test_params_null(self):
        """Using 'params': null is *not* valid under the schema."""
        self.assertErrorEquals(
            JSONRPC_INVALID_REQUEST_HTTP_CODE,
            JSONRPC_INVALID_REQUEST_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': None})
        )

    def test_id_null(self):
        """Using 'id': null *is* valid under the schema."""
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'id': None})
        )

    # MethodNotFound

    def test_method_not_found(self):
        self.assertErrorEquals(
            JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            JSONRPC_METHOD_NOT_FOUND_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'get'})
        )

    def test_trying_to_call_magic_method(self):
        self.assertErrorEquals(
            JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            JSONRPC_METHOD_NOT_FOUND_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': '__init__'})
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the params can come through

    # method_only

    def test_method_only_params_omitted(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only'})
        )

    def test_method_only_params_empty(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': []})
        )

    def test_method_only_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1]})
        )

    def test_method_only_two_args(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2]})
        )

    def test_method_only_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': {'foo': 'bar'}})
        )

    def test_method_only_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2, {'foo': 'bar'}]})
        )

    # one_positional

    def test_one_positional_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional'})
        )

    def test_one_positional_one_arg(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1]})
        )

    def test_one_positional_two_args(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2]})
        )

    def test_one_positional_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': {'foo': 'bar'}})
        )

    def test_one_positional_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2, {'foo': 'bar'}]})
        )

    # two_positionals

    def test_two_positionals_ok(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, 2]})
        )

    def test_two_positionals_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals'})
        )

    def test_two_positionals_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1]})
        )

    def test_two_positionals_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': {'foo': 'bar'}})
        )

    def test_two_positionals_both(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, {'foo': 'bar'}]})
        )

    # just_args

    def test_just_args_ok(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, 2]})
        )

    def test_just_args_params_omitted(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args'})
        )

    def test_just_args_one_arg(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1]})
        )

    def test_just_args_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': {'foo': 'bar'}})
        )

    def test_just_args_both(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, {'foo': 'bar'}]})
        )

    # just_kwargs

    def test_just_kwargs_ok(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_just_kwargs_params_omitted(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs'})
        )

    def test_just_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1]})
        )

    def test_just_kwargs_kwargs(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_just_kwargs_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_args

    def test_positionals_with_args_ok(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': ['foo', 42]})
        )

    def test_positionals_with_args_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args'})
        )

    def test_positionals_with_args_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1]})
        )

    def test_positionals_with_args_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': {'foo': 'bar'}})
        )

    def test_positionals_with_args_both(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_kwargs

    def test_positionals_with_kwargs_ok(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})
        )

    def test_positionals_with_kwargs_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs'})
        )

    def test_positionals_with_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1]})
        )

    def test_positionals_with_kwargs_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_positionals_with_kwargs_both(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_args_and_kwargs

    def test_positionals_with_args_and_kwargs_ok(self):
        self.assertNoContent(
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})
        )

    def test_positionals_with_args_and_kwargs_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs'})
        )

    def test_positionals_with_args_and_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1]})
        )

    def test_positionals_with_args_and_kwargs_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_positionals_with_args_and_kwargs_both(self):
        self.assertNoContent(
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

    def test_full_function_not_lambda(self):
        self.assertResultEquals(
            'Smith',
            dispatch({'jsonrpc': '2.0', 'method': 'lookup_surname', 'params': {'firstname': 'John'}, 'id': 1})
        )

    def test_class_method(self):
        self.assertResultEquals(
            5,
            dispatch({'jsonrpc': '2.0', 'method': 'get_5', 'id': 1})
        )

    def test_raising_jsonrpcservererror(self):
        response = dispatch({'jsonrpc': '2.0', 'method': 'raise_jsonrpcservererror'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Database error',
            response
        )
        # Because the more_info was not passed, there should be no 'data'
        self.assertNotIn('data', response[0]['error'])

    def test_raising_jsonrpcservererror_with_more_info(self):
        response = dispatch({'jsonrpc': '2.0', 'method': 'raise_jsonrpcservererror'}, more_info=True)
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Database error',
            response
        )
        # Because the more_info was passed, there should be 'data'.
        self.assertEqual('Column "Insecure" does not exist', response[0]['error']['data'])


    def test_raising_other_error(self):
        response = dispatch({'jsonrpc': '2.0', 'method': 'raise_other_error'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Server error',
            response
        )
        # Because the more_info was not passed, there should be no 'data'
        self.assertNotIn('data', response[0]['error'])

    def test_raising_other_error_with_more_info(self):
        response = dispatch({'jsonrpc': '2.0', 'method': 'raise_other_error'}, more_info=True)
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Server error',
            response
        )
        # Because the more_info was passed, there should be 'data'.
        self.assertEqual('Value too low', response[0]['error']['data'])


if __name__ == '__main__':
    main()
