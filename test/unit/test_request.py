"""test_request.py"""
#pylint:disable=missing-docstring,line-too-long

from unittest import TestCase, main

from jsonrpcserver.request import _string_to_dict, _get_arguments, Request
from jsonrpcserver.exceptions import ParseError, InvalidRequest, InvalidParams


class TestStringToDict(TestCase):

    def test_ok(self):
        self.assertEqual({'jsonrpc': '2.0', 'method': 'foo'}, _string_to_dict(
            '{"jsonrpc": "2.0", "method": "foo"}'))

    def test_invalid(self):
        with self.assertRaises(ParseError):
            _string_to_dict('{"jsonrpc": "2.0}')


class TestGetArguments(TestCase):

    def test_none(self):
        self.assertEqual((None, None), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo'}))

    def test_positional(self):
        self.assertEqual(([2, 3], None), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo', 'params': [2, 3]}))

    def test_keyword(self):
        self.assertEqual((None, {'foo': 'bar'}), _get_arguments(
            {'jsonrpc': '2.0', 'method': 'foo', 'params': {'foo': 'bar'}}))

    def test_invalid_none(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': None})

    def test_invalid_numeric(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': 5})

    def test_invalid_string(self):
        with self.assertRaises(InvalidParams):
            _get_arguments({'jsonrpc': '2.0', 'method': 'foo', 'params': 'str'})


class TestRequestInit(TestCase):

    def test_ok(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual('foo', r.method_name)

    def test_string(self):
        r = Request('{"jsonrpc": "2.0", "method": "foo"}')
        self.assertEqual('foo', r.method_name)

    def test_positional_args(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'params': [2, 3]})
        self.assertEqual([2, 3], r.args)

    def test_keyword_args(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'params': {'foo': 'bar'}})
        self.assertEqual({'foo': 'bar'}, r.kwargs)

    def test_request_id(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 99})
        self.assertEqual(99, r.request_id)

    def test_request_id_notification(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertEqual(None, r.request_id)

    def test_parse_error(self):
        with self.assertRaises(ParseError):
            Request('{jsonrpc: 2.0}')

    def test_invalid_request(self):
        with self.assertRaises(InvalidRequest):
            Request({'jsonrpc': '2.0'})


class TestRequestIsNotification(TestCase):

    def test_true(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo'})
        self.assertTrue(r.is_notification)

    def test_false(self):
        r = Request({'jsonrpc': '2.0', 'method': 'foo', 'id': 99})
        self.assertFalse(r.is_notification)


if __name__ == '__main__':
    main()
