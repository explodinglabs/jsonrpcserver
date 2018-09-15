from functools import partial
from unittest.mock import patch

import pytest

from jsonrpcserver.methods import Methods


def test_add_function():
    def foo():
        pass
    methods = Methods()
    methods.add(foo)
    assert methods.items["foo"] is foo

def test_add_non_callable():
    methods = Methods()
    with pytest.raises(AssertionError):
        methods.add(None, "ping")

def test_add_function_custom_name():
    def foo():
        pass

    methods = Methods()
    methods.add(foo, "foobar")
    assert methods.items["foobar"] is foo

def test_add_lambda_no_name():
    add = lambda x, y: x + y
    methods = Methods()
    methods.add(add)  # Lambda's __name__ will be '<lambda>'!
    assert "add" not in methods.items

def test_add_lambda_renamed():
    add = lambda x, y: x + y
    add.__name__ = "add"
    methods = Methods()
    methods.add(add)
    methods.items["add"] is add

def test_add_lambda_custom_name():
    add = lambda x, y: x + y
    methods = Methods()
    methods.add(add, "add")
    assert methods.items["add"] is add

def test_add_partial_no_name():
    six = partial(lambda x: x + 1, 5)
    methods = Methods()
    with pytest.raises(AttributeError):
        methods.add(six)  # Partial has no __name__ !

def test_add_partial_renamed():
    six = partial(lambda x: x + 1, 5)
    six.__name__ = "six"
    methods = Methods()
    methods.add(six)
    assert methods.items["six"] is six

def test_add_partial_custom_name():
    six = partial(lambda x: x + 1, 5)
    methods = Methods()
    methods.add(six, "six")
    assert methods.items["six"] is six

def test_add_static_method():
    class FooClass(object):
        @staticmethod
        def foo():
            return "bar"

    methods = Methods()
    methods.add(FooClass.foo)
    assert methods.items["foo"] is FooClass.foo

def test_add_static_method_custom_name():
    class FooClass(object):
        @staticmethod
        def foo():
            return "bar"

    methods = Methods()
    methods.add(FooClass.foo, "custom")
    assert methods.items["custom"] == FooClass.foo

def test_add_instance_method():
    class FooClass(object):
        def foo(self):
            return "bar"

    methods = Methods()
    methods.add(FooClass().foo)
    assert methods.items["foo"].__call__() is "bar"

def test_add_instance_method_custom_name():
    class Foo(object):
        def __init__(self, name):
            self.name = name

        def get_name(self):
            return self.name

    obj1 = Foo("a")
    obj2 = Foo("b")
    methods = Methods()
    methods.add(obj1.get_name, "custom1")
    methods.add(obj2.get_name, "custom2")
    # Can't use assertIs, so check the outcome is as expected
    assert methods.items["custom1"].__call__() == "a"
    assert methods.items["custom2"].__call__() == "b"


def test_add_function_via_decorator():
    methods = Methods()
    @methods.add
    def foo():
        pass
    assert methods.items["foo"] is foo


def test_add_static_method_via_decorator():
    methods = Methods()

    class FooClass(object):
        @staticmethod
        @methods.add
        def foo():
            return "bar"

    assert methods.items["foo"] is FooClass.foo


def test_get():
    def cat():
        pass

    def dog():
        pass

    methods = Methods()
    methods.add(cat)
    methods.add(dog)
    assert methods.get("cat") == cat
    assert methods.get("dog") == dog


@patch("http.server.HTTPServer.serve_forever")
def test_serve_forever(*_):
    methods = Methods()
    methods.serve_forever()
