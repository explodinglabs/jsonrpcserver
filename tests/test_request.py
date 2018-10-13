import json

import pytest

from jsonrpcserver.request import (
    NOID,
    Request,
    convert_camel_case_keys,
    convert_camel_case_string,
    get_arguments,
)


def test_convert_camel_case_string():
    assert convert_camel_case_string("fooBar") == "foo_bar"


def test_convert_camel_case_keys():
    dictionary = {"fooKey": 1, "aDict": {"fooKey": 1, "barKey": 2}}
    assert convert_camel_case_keys(dictionary) == {
        "foo_key": 1,
        "a_dict": {"foo_key": 1, "bar_key": 2},
    }


def test_get_arguments_none():
    with pytest.raises(AssertionError):
        get_arguments(None)


def test_get_arguments_invalid():
    with pytest.raises(AssertionError):
        assert get_arguments(5)


def test_get_arguments_positional():
    assert get_arguments([2, 3]) == ([2, 3], {})


def test_get_arguments_keyword():
    assert get_arguments({"foo": "bar"}) == ([], {"foo": "bar"})


def test_get_arguments_invalid_string():
    with pytest.raises(AssertionError):
        get_arguments("str")


# With the "context" argument
def test_get_arguments_positional_with_context():
    args = get_arguments(["foo"], context="bar")
    assert args == (["foo"], {"context": "bar"})


def test_get_arguments_keyword_with_context():
    args = get_arguments({"foo": "bar"}, context="baz")
    assert args == ([], {"foo": "bar", "context": "baz"})


def test_request():
    assert Request(method="foo").method == "foo"


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


def test_request_no_args():
    req = Request(method="foo")
    assert req.args == []
    assert req.kwargs == {}


def test_request_positional_args():
    req = Request(method="foo", params=[2, 3])
    assert req.args == [2, 3]
    assert req.kwargs == {}


def test_request_keyword_args():
    req = Request(method="foo", params={"foo": "bar"})
    assert req.args == []
    assert req.kwargs == {"foo": "bar"}


def test_request_id():
    assert Request(method="foo", id=99).id == 99


def test_request_no_id():
    request = Request({"jsonrpc": "2.0", "method": "foo"})
    assert request.id is NOID


def test_request_from_string():
    request = Request(**json.loads('{"jsonrpc": "2.0", "method": "foo", "id": 1}'))
    assert request.jsonrpc == "2.0"
    assert request.method == "foo"
    assert request.id == 1


def test_request_convert_camel_case():
    request = Request(**{"jsonrpc": "2.0", "method": "fooBar", "params": {"fooBar": 1}}, convert_camel_case=True)
    assert request.method == "foo_bar"
