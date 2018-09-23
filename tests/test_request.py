import json
import logging
from functools import partial
from unittest import TestCase

import pytest

from jsonrpcserver import status
from jsonrpcserver.methods import Methods
from jsonrpcserver.request import (
    NOID,
    Request,
    convert_camel_case_keys,
    convert_camel_case_string,
    get_arguments,
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


def test_request():
    req = Request(method="foo")
    assert req.method == "foo"


def test_request_invalid():
    # Should never happen, because the incoming request string is passed through the
    # jsonrpc schema before creating a Request
    pass


def test_notification_true():
    request = Request(method="foo")
    assert request.is_notification is True


def test_notification_false():
    request = Request(method="foo", id=99)
    assert request.is_notification is False


def test_request_positional_args():
    req = Request(method="foo", params=[2, 3])
    assert req.args == [2, 3]
    assert req.kwargs is None


def test_request_keyword_args():
    req = Request(method="foo", params={"foo": "bar"})
    assert req.args is None
    assert req.kwargs == {"foo": "bar"}


def test_id():
    assert Request(method="foo", id=99).id == 99


def test_no_id():
    request = Request({"jsonrpc": "2.0", "method": "foo"})
    assert request.id is NOID


def test_request_from_string():
    request = Request(**json.loads('{"jsonrpc": "2.0", "method": "foo", "id": 1}'))
    assert request.jsonrpc == "2.0"
    assert request.method == "foo"
    assert request.id == 1
