import logging

from jsonrpcserver.log import _trim_message, _trim_string, _trim_values, log_


def test_trim_string():
    assert "..." in _trim_string("foo" * 100)


def test_trim_string_already_short():
    assert _trim_string("foo") == "foo"


def test_trim_values():
    message = _trim_values({"list": [0] * 100})
    assert "..." in message["list"]


def test_trim_values_nested():
    message = _trim_values({"obj": {"obj2": {"string2": "foo" * 100}}})
    assert "..." in message["obj"]["obj2"]["string2"]


def test_trim_values_batch():
    message = _trim_values([{"list": [0] * 100}])
    assert "..." in message[0]["list"]


def test_trim_values_bool():
    message = _trim_values({"list": True})
    assert message["list"] is True


def test_trim_message():
    message = _trim_message('{"val": "%s"}' % ("foo" * 100))
    assert "..." in message


def test_trim_message_invalid_json():
    message = _trim_message("foo" * 100)
    assert "..." in message


def test_log():
    log_("foo", logging.getLogger(), trim=True)
