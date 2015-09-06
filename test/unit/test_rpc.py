"""test_rpc.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

from unittest import TestCase, main
import json

from jsonrpcserver.rpc import rpc_success_response, rpc_error_response, \
    sort_response


class TestRpc(TestCase):

    # sort_response
    def test_sort_response_success(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "result": 5, "id": 1}',
            json.dumps(sort_response({'id': 1, 'result': 5, 'jsonrpc': '2.0'})),
        )

    def test_sort_response_error(self):
        self.assertEqual(
            '{"jsonrpc": "2.0", "error": {"code": -320000}, "id": 1}',
            json.dumps(sort_response({'error': {"code": -320000}, 'id': 1, 'jsonrpc': '2.0'})),
        )

    # rpc_success_response()
    def test_result_with_no_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": None, "id": 1},
            rpc_success_response(1, None)
        )

    def test_result_with_string_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": "foo", "id": 1},
            rpc_success_response(1, 'foo')
        )

    def test_result_with_int_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": 42, "id": 1},
            rpc_success_response(1, 42)
        )

    def test_result_with_list_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": ["foo", {'foo': 'bar', 'answer': 42}, [1, 2, 3]], "id": 1},
            rpc_success_response(1, ['foo', {'foo': 'bar', 'answer': 42}, [1, 2, 3]])
        )

    def test_result_with_dict_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": {'foo': 'bar', 'answer': 42, 'list': ['One', 2]}, "id": 1},
            rpc_success_response(1, {'foo': 'bar', 'answer': 42, 'list': ['One', 2]})
        )

    # rpc_error_response()
    def test_error_with_no_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error"}, "id": 1},
            rpc_error_response(1, -32000, 'There was an error')
        )

    def test_error_with_string_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": "Test"}, "id": 1},
            rpc_error_response(1, -32000, 'There was an error', 'Test')
        )

    def test_error_with_list_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": ["One", "Two", 3]}, "id": 1},
            rpc_error_response(1, -32000, 'There was an error', ['One', 'Two', 3])
        )

    def test_error_with_dict_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": {"Foo": "Bar", "Answer": 42}}, "id": 1},
            rpc_error_response(1, -32000, 'There was an error', {'Foo': 'Bar', 'Answer': 42})
        )


if __name__ == '__main__':
    main()
