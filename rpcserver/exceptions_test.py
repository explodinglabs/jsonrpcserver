"""exceptions_test.py"""
# pylint: disable=missing-docstring,line-too-long

from nose.tools import assert_raises # pylint: disable=no-name-in-module

from . import exceptions

def test_ParseError():
    with assert_raises(exceptions.ParseError):
        raise exceptions.ParseError()

def test_InvalidRequest():
    with assert_raises(exceptions.InvalidRequest):
        raise exceptions.InvalidRequest(dict({'id': 'Missing'}))

def test_InvalidParams():
    with assert_raises(exceptions.InvalidParams):
        raise exceptions.InvalidParams()

def test_MethodNotFound():
    with assert_raises(exceptions.MethodNotFound):
        raise exceptions.MethodNotFound()
