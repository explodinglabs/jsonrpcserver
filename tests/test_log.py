import logging
from unittest.mock import patch

from jsonrpcserver.log import configure_logger, log, trim_message


@patch('logging.root.handlers', [])
def test_configure_logger(*_):
    # Override root handlers, because pytest adds one
    logger = logging.getLogger('foo')
    configure_logger(logger, "%(message)s")
    assert logger.hasHandlers()
    assert logging.getLevelName(logger.level) == 'INFO'
    assert logger.handlers[0].formatter._fmt == "%(message)s"


def test_log(caplog):
    logging.getLogger().setLevel(logging.INFO)
    logger = logging.getLogger('foo')
    log(logger, logging.INFO, 'foo')
    assert 'foo' in caplog.text


def test_trim_message():
    import json
    # test string abbreviation
    message = trim_message("blah" * 100)
    assert '...' in message
    # test list abbreviation
    message = trim_message(json.dumps({"list": [0]*100}))
    assert '...' in message
    # test nested abbreviation
    message = trim_message(json.dumps({
        "obj": {
            "list": [0] * 100,
            "string": "blah" * 100,
            "obj2": {
                "string2": "blah" * 100,
            }
        }
    }))
    assert '...' in json.loads(message)['obj']['obj2']['string2']
