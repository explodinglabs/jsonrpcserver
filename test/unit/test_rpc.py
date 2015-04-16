"""test_rpc.py"""
#pylint:disable=missing-docstring,line-too-long,too-many-public-methods

from unittest import TestCase, main

from jsonrpcserver import rpc


class TestRpc(TestCase):

    # rpc.result()

    def test_result_with_no_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": None, "id": 1},
            rpc.result(1, None)
        )

    def test_result_with_string_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": "foo", "id": 1},
            rpc.result(1, 'foo')
        )

    def test_result_with_int_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": 42, "id": 1},
            rpc.result(1, 42)
        )

    def test_result_with_list_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": ["foo", {'foo': 'bar', 'answer': 42}, [1, 2, 3]], "id": 1},
            rpc.result(1, ['foo', {'foo': 'bar', 'answer': 42}, [1, 2, 3]])
        )

    def test_result_with_dict_as_result(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "result": {'foo': 'bar', 'answer': 42, 'list': ['One', 2]}, "id": 1},
            rpc.result(1, {'foo': 'bar', 'answer': 42, 'list': ['One', 2]})
        )

    # rpc.error()

    def test_error_with_no_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error"}, "id": 1},
            rpc.error(1, -32000, 'There was an error')
        )

    def test_error_with_string_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": "Test"}, "id": 1},
            rpc.error(1, -32000, 'There was an error', 'Test')
        )

    def test_error_with_list_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": ["One", "Two", 3]}, "id": 1},
            rpc.error(1, -32000, 'There was an error', ['One', 'Two', 3])
        )

    def test_error_with_dict_as_data(self):
        self.assertEqual(
            {"jsonrpc": "2.0", "error": {"code": -32000, "message": "There was an error", "data": {"Foo": "Bar", "Answer": 42}}, "id": 1},
            rpc.error(1, -32000, 'There was an error', {'Foo': 'Bar', 'Answer': 42})
        )

if __name__ == '__main__':
    main()
