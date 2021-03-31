import json

import pytest

from jsonrpcserver.request import NOID, Request, is_notification


def test_request():
    assert Request(method="foo", params=[], id=1).method == "foo"


def test_request_invalid():
    # Should never happen, because the incoming request string is passed through the
    # jsonrpc schema before creating a Request
    pass


def test_is_notification_true():
    assert is_notification(Request(method="foo", params=[], id=NOID)) is True


def test_is_notification_false():
    assert is_notification(Request(method="foo", params=[], id=1)) is False
