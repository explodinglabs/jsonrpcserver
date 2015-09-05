"""test_dispatcher.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods,no-init,unused-argument

from unittest import TestCase, main, skip

from jsonrpcserver.dispatcher import Dispatcher
from jsonrpcserver.exceptions import ServerError
from jsonrpcserver.status import JSONRPC_INVALID_PARAMS_TEXT, \
    JSONRPC_INVALID_PARAMS_HTTP_CODE, JSONRPC_METHOD_NOT_FOUND_HTTP_CODE, \
    JSONRPC_METHOD_NOT_FOUND_TEXT, JSONRPC_INVALID_REQUEST_TEXT, \
    JSONRPC_INVALID_REQUEST_HTTP_CODE, JSONRPC_SERVER_ERROR_HTTP_CODE, \
    JSONRPC_SERVER_ERROR_TEXT

tests = Dispatcher()

tests.register_method(pow)
tests.register_method(lambda: None, 'method_only')
tests.register_method(lambda string: None, 'one_positional')
tests.register_method(lambda one, two: None, 'two_positionals')
tests.register_method(lambda *args: None, 'just_args')
tests.register_method(lambda **kwargs: None, 'just_kwargs')
tests.register_method(lambda one, two, *args: None, 'positionals_with_args')
tests.register_method(lambda one, two, **kwargs: None, 'positionals_with_kwargs')
tests.register_method(lambda one, two, *args, **kwargs: None, 'positionals_with_args_and_kwargs')
tests.register_method(lambda one, two: one + two, 'add')
tests.register_method(lambda string: string.upper(), 'uppercase')

@tests.method('get')
def get(**kwargs):
    """Test using a full function, not a lambda"""
    if kwargs['firstname'] == 'John':
        return 'Smith'

@tests.method('raise_servererror')
def raise_servererror():
    raise ServerError('Column "Insecure" does not exist')

@tests.method('raise_other_error')
def raise_other_error():
    raise ValueError('Value too low')

class HandleRequests:
    """Test using a class method, not a function"""
    @staticmethod
    @tests.method('get_5')
    def get_5():
        return 5


class TestDispatch(TestCase):

    def setUp(self):
        tests.debug = False

    def assertNoContent(self, response):
        result, status = response
        self.assertEqual(None, result)
        self.assertEqual(204, status)

    def assertResultEquals(self, expected_result, response):
        result, status = response
        self.assertIn('result', result)
        self.assertEqual(200, status)
        self.assertEqual(expected_result, result['result'])

    def assertErrorEquals(self, expected_status, expected_result, response):
        result, status = response
        self.assertIn('error', result)
        self.assertEqual(expected_result, result['error']['message'])
        self.assertEqual(expected_status, status)

    # InvalidRequest

    def test_dispatch_missing_jsonrpc_property(self):
        """jsonrpc is a required property"""
        self.assertErrorEquals(
            JSONRPC_INVALID_REQUEST_HTTP_CODE,
            JSONRPC_INVALID_REQUEST_TEXT,
            tests.dispatch({'jsonrp': '2.0', 'method': 'get'})
        )

    def test_dispatch_params_null(self):
        """Using 'params': null is *not* valid under the schema."""
        self.assertErrorEquals(
            JSONRPC_INVALID_REQUEST_HTTP_CODE,
            JSONRPC_INVALID_REQUEST_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': None})
        )

    def test_dispatch_id_null(self):
        """Using 'id': null *is* valid under the schema."""
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'id': None})
        )

    # MethodNotFound

    def test_dispatch_method_not_found(self):
        self.assertErrorEquals(
            JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            JSONRPC_METHOD_NOT_FOUND_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'no_such_method'})
        )

    def test_dispatch_trying_to_call_magic_method(self):
        self.assertErrorEquals(
            JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            JSONRPC_METHOD_NOT_FOUND_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': '__init__'})
        )

    # pow

    @skip('inspect module seemingly wont allow getcallargs on a builtin')
    def test_dispatch_pow(self):
        self.assertResultEquals(
            8,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'pow', 'params': [2, 3], 'id': 1})
        )

    # InvalidParams - this requires lots of testing because there are many ways
    # the params can come through

    # method_only

    def test_dispatch_method_only_params_omitted(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only'})
        )

    def test_dispatch_method_only_params_empty(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': []})
        )

    def test_dispatch_method_only_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1]})
        )

    def test_dispatch_method_only_two_args(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2]})
        )

    def test_dispatch_method_only_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_method_only_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'method_only', 'params': [1, 2, {'foo': 'bar'}]})
        )

    # one_positional

    def test_dispatch_one_positional_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'one_positional'})
        )

    def test_dispatch_one_positional_one_arg(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1]})
        )

    def test_dispatch_one_positional_two_args(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2]})
        )

    def test_dispatch_one_positional_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_one_positional_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'one_positional', 'params': [1, 2, {'foo': 'bar'}]})
        )

    # two_positionals

    def test_dispatch_two_positionals_ok(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, 2]})
        )

    def test_dispatch_two_positionals_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'two_positionals'})
        )

    def test_dispatch_two_positionals_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1]})
        )

    def test_dispatch_two_positionals_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_two_positionals_both(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'two_positionals', 'params': [1, {'foo': 'bar'}]})
        )

    # just_args

    def test_dispatch_just_args_ok(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, 2]})
        )

    def test_dispatch_just_args_params_omitted(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_args'})
        )

    def test_dispatch_just_args_one_arg(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1]})
        )

    def test_dispatch_just_args_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_just_args_both(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_args', 'params': [1, {'foo': 'bar'}]})
        )

    # just_kwargs

    def test_dispatch_just_kwargs_ok(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_just_kwargs_params_omitted(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs'})
        )

    def test_dispatch_just_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1]})
        )

    def test_dispatch_just_kwargs_kwargs(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_just_kwargs_both(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'just_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_args

    def test_dispatch_positionals_with_args_ok(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': ['foo', 42]})
        )

    def test_dispatch_positionals_with_args_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args'})
        )

    def test_dispatch_positionals_with_args_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1]})
        )

    def test_dispatch_positionals_with_args_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_positionals_with_args_both(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_kwargs

    def test_dispatch_positionals_with_kwargs_ok(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})
        )

    def test_dispatch_positionals_with_kwargs_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs'})
        )

    def test_dispatch_positionals_with_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1]})
        )

    def test_dispatch_positionals_with_kwargs_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_positionals_with_kwargs_both(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # positionals_with_args_and_kwargs

    def test_dispatch_positionals_with_args_and_kwargs_ok(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': ['foo', 42, {'foo': 'bar'}]})
        )

    def test_dispatch_positionals_with_args_and_kwargs_params_omitted(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs'})
        )

    def test_dispatch_positionals_with_args_and_kwargs_one_arg(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1]})
        )

    def test_dispatch_positionals_with_args_and_kwargs_kwargs(self):
        self.assertErrorEquals(
            JSONRPC_INVALID_PARAMS_HTTP_CODE,
            JSONRPC_INVALID_PARAMS_TEXT,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': {'foo': 'bar'}})
        )

    def test_dispatch_positionals_with_args_and_kwargs_both(self):
        self.assertNoContent(
            tests.dispatch({'jsonrpc': '2.0', 'method': 'positionals_with_args_and_kwargs', 'params': [1, {'foo': 'bar'}]})
        )

    # Test return results

    def test_dispatch_add_two_numbers(self):
        self.assertResultEquals(
            3,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'add', 'params': [1, 2], 'id': 1})
        )

    def test_dispatch_uppercase(self):
        self.assertResultEquals(
            'TEST',
            tests.dispatch({'jsonrpc': '2.0', 'method': 'uppercase', 'params': ['test'], 'id': 1})
        )

    def test_dispatch_full_function_not_lambda(self):
        self.assertResultEquals(
            'Smith',
            tests.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {'firstname': 'John'}, 'id': 1})
        )

    def test_dispatch_class_method(self):
        self.assertResultEquals(
            5,
            tests.dispatch({'jsonrpc': '2.0', 'method': 'get_5', 'id': 1})
        )

    def test_dispatch_raising_servererror(self):
        response = tests.dispatch({'jsonrpc': '2.0', 'method': 'raise_servererror'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            JSONRPC_SERVER_ERROR_TEXT,
            response
        )
        # Because the debug was not passed, there should be no 'data'
        self.assertNotIn('data', response[0]['error'])

    def test_dispatch_raising_servererror_with_debug(self):
        tests.debug = True
        response = tests.dispatch({'jsonrpc': '2.0', 'method': 'raise_servererror'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            JSONRPC_SERVER_ERROR_TEXT,
            response
        )
        # Because debugging is on, there should be 'data'.
        self.assertEqual('Column "Insecure" does not exist', response[0]['error']['data'])


    def test_dispatch_raising_other_error(self):
        response = tests.dispatch({'jsonrpc': '2.0', 'method': 'raise_other_error'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Server error',
            response
        )
        # Because debugging is off, there should be no 'data'
        self.assertNotIn('data', response[0]['error'])

    def test_dispatch_raising_other_error_with_debug(self):
        tests.debug = True
        response = tests.dispatch({'jsonrpc': '2.0', 'method': 'raise_other_error'})
        self.assertErrorEquals(
            JSONRPC_SERVER_ERROR_HTTP_CODE,
            'Server error',
            response
        )
        # Because debug is on, there should be 'data'.
        self.assertEqual('See server logs', response[0]['error']['data'])

    # dispatch_str
    def test_dispatch_str_method_not_found(self):
        self.assertErrorEquals(
            JSONRPC_METHOD_NOT_FOUND_HTTP_CODE,
            JSONRPC_METHOD_NOT_FOUND_TEXT,
            tests.dispatch_str('{"jsonrpc": "2.0", "method": "no_such_method"}')
        )


if __name__ == '__main__':
    main()
