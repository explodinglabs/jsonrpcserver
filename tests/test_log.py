from jsonrpcserver.log import _trim_message, _trim_string, _trim_values


def test_trim_string():
    message = _trim_string("foo" * 100)
    assert "..." in message


def test_trim_values():
    message = _trim_values({"list": [0] * 100})
    assert "..." in message["list"]


def test_trim_values_nested():
    message = _trim_values({"obj": {"obj2": {"string2": "foo" * 100}}})
    assert "..." in message["obj"]["obj2"]["string2"]


def test_trim_values_batch():
    message = _trim_values([{"list": [0] * 100}])
    assert "..." in message[0]["list"]


def test_trim_message():
    message = _trim_message("foo" * 100)
    assert "..." in message
