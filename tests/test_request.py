import logging
from functools import partial
from unittest import TestCase

import pytest

from jsonrpcserver import status
from jsonrpcserver.methods import Methods
from jsonrpcserver.request import (
    convert_camel_case_string,
    convert_camel_case_keys,
    get_arguments,
    Request,
    validate_arguments_against_signature,
    NOID,
)
from jsonrpcserver.response import ErrorResponse, NotificationResponse


def test_convert_camel_case_string():
    assert convert_camel_case_string("fooBar") == "foo_bar"


def test_convert_camel_case_keys():
    dictionary = {"fooKey": 1, "aDict": {"fooKey": 1, "barKey": 2}}
    assert convert_camel_case_keys(dictionary) == {
        "foo_key": 1,
        "a_dict": {"foo_key": 1, "bar_key": 2},
    }


def test_validate_no_arguments():
    validate_arguments_against_signature(lambda: None, None, None)


def test_validate_no_arguments_too_many_positionals():
    with pytest.raises(TypeError):
        validate_arguments_against_signature(lambda: None, ["foo"], None)


def test_validate_positionals():
    validate_arguments_against_signature(lambda x: None, [1], None)


def test_validate_positionals_not_passed():
    with pytest.raises(TypeError):
        validate_arguments_against_signature(lambda x: None, None, {"foo": "bar"})


def test_validate_keywords():
    validate_arguments_against_signature(lambda **kwargs: None, None, {"foo": "bar"})


def test_validate_object_method():
    class FooClass:
        def foo(self, one, two):
            return "bar"

    validate_arguments_against_signature(FooClass().foo, ["one", "two"], None)


def test_get_arguments_none():
    assert get_arguments(None) == (None, None)


def test_get_arguments_positional():
    assert get_arguments([2, 3]) == ([2, 3], None)


def test_get_arguments_keyword():
    assert get_arguments({"foo": "bar"}) == (None, {"foo": "bar"})


def test_get_arguments_invalid_numeric():
    with pytest.raises(TypeError):
        get_arguments(5)


def test_get_arguments_invalid_string():
    with pytest.raises(TypeError):
        get_arguments("str")


# With the "context" argument
def test_get_arguments_no_arguments_with_context():
    args = get_arguments(None, context="foo")
    assert args == (None, {"context": "foo"})


def test_get_arguments_positional_with_context():
    args = get_arguments(["foo"], context="bar")
    assert args == (["foo"], {"context": "bar"})


def test_get_arguments_keyword_with_context():
    args = get_arguments({"foo": "bar"}, context="baz")
    assert args == (None, {"foo": "bar", "context": "baz"})


def test_notification_true():
    request = Request({"jsonrpc": "2.0", "method": "foo"})
    assert request.is_notification is True


def test_notification_false():
    request = Request({"jsonrpc": "2.0", "method": "foo", "id": 99})
    assert request.is_notification is False


def test_request():
    req = Request({"jsonrpc": "2.0", "method": "foo"})
    assert req.method_name == "foo"


def test_request_invalid():
    # Should never happen, because the incoming request is passed through the jsonrpc
    # schema before creating a Request
    pass


def test_request_positional_args():
    req = Request({"jsonrpc": "2.0", "method": "foo", "params": [2, 3]})
    assert req.args == [2, 3]
    assert req.kwargs is None


def test_request_keyword_args():
    req = Request({"jsonrpc": "2.0", "method": "foo", "params": {"foo": "bar"}})
    assert req.args is None
    assert req.kwargs == {"foo": "bar"}


def test_request_id():
    assert Request({"jsonrpc": "2.0", "method": "foo", "id": 99}).request_id == 99


def test_request_id_notification():
    request = Request({"jsonrpc": "2.0", "method": "foo"})
    assert request.request_id is NOID


def test_request_convert_camel_case():
    req = Request(
        {
            "jsonrpc": "2.0",
            "method": "fooMethod",
            "params": {"fooParam": 1, "aDict": {"barParam": 1}},
        },
        convert_camel_case=True,
    )
    assert req.method_name == "foo_method"
    assert req.kwargs == {"foo_param": 1, "a_dict": {"bar_param": 1}}


def test_request_convert_camel_case_positional_args():
    req = Request(
        {"jsonrpc": "2.0", "method": "foo", "params": ["Camel", "Case"]},
        convert_camel_case=True,
    )
    assert req.args == ["Camel", "Case"]
