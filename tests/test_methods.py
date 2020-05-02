from functools import partial

import pytest

from jsonrpcserver.methods import Methods, add, validate_args, lookup
from jsonrpcserver.exceptions import MethodNotFoundError, InvalidParamsError


def test_validate_no_arguments():
    validate_args(lambda: None)


def test_validate_no_arguments_too_many_positionals():
    with pytest.raises(InvalidParamsError):
        validate_args(lambda: None, "foo")


def test_validate_positionals():
    validate_args(lambda x: None, 1)


def test_validate_positionals_not_passed():
    with pytest.raises(InvalidParamsError):
        validate_args(lambda x: None, foo="bar")


def test_validate_keywords():
    validate_args(lambda **kwargs: None, foo="bar")


def test_validate_object_method():
    class FooClass:
        def foo(self, one, two):
            return "bar"

    validate_args(FooClass().foo, "one", "two")


def test_add_function():
    def foo():
        pass

    methods = Methods(foo)
    assert methods.items["foo"] is foo


def test_add_no_name():
    # AttibuteError will be raised if a method is passed as a positional argument with
    # no __name__ attribute
    class C(object):
        def __call__(self):
            return None

    with pytest.raises(AttributeError):
        Methods(C())


def test_add_non_callable():
    with pytest.raises(AssertionError):
        Methods(None)


def test_add_func_named():
    def foo():
        pass

    assert "bar" in Methods(bar=foo).items


def test_add_lambda_named():
    assert "foo" in Methods(foo=lambda: None).items


def test_add_lambda_no_name():
    lmb = lambda x, y: x + y
    methods = Methods(lmb)
    # The lambda's __name__ will be '<lambda>'!
    assert "<lambda>" in methods.items


def test_add_partial_no_name():
    six = partial(lambda x: x + 1, 5)
    methods = Methods()
    with pytest.raises(AttributeError):
        methods.add(six)  # Partial has no __name__ !


def test_add_partial_renamed():
    six = partial(lambda x: x + 1, 5)
    six.__name__ = "six"
    assert Methods(six).items["six"] is six


def test_add_partial_custom_name():
    six = partial(lambda x: x + 1, 5)
    assert Methods(six=six).items["six"] is six


def test_add_static_method():
    class FooClass:
        @staticmethod
        def foo():
            return "bar"

    assert Methods(FooClass.foo).items["foo"] is FooClass.foo


def test_add_static_method_custom_name():
    class FooClass:
        @staticmethod
        def foo():
            return "bar"

    assert Methods(custom=FooClass.foo).items["custom"] == FooClass.foo


def test_add_instance_method():
    class FooClass:
        def foo(self):
            return "bar"

    assert Methods(FooClass().foo).items["foo"].__call__() is "bar"


def test_add_instance_method_custom_name():
    class Foo:
        def __init__(self, name):
            self.name = name

        def get_name(self):
            return self.name

    obj1 = Foo("a")
    obj2 = Foo("b")
    methods = Methods(custom1=obj1.get_name, custom2=obj2.get_name)
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

    class FooClass:
        @staticmethod
        @methods.add
        def foo():
            return "bar"

    assert methods.items["foo"] is FooClass.foo


def test_global_methods_add():
    # The global "add" function which wraps global_methods.add
    add(lambda x: y)


def test_get():
    def cat():
        pass

    def dog():
        pass

    methods = Methods(cat, dog)
    assert methods.items["cat"] == cat
    assert methods.items["dog"] == dog


def test_lookup():
    def foo():
        pass

    methods = Methods()
    methods.items["foo"] = foo

    assert lookup(methods, "foo") is foo


def test_lookup_failure():
    methods = Methods()

    with pytest.raises(MethodNotFoundError):
        lookup(methods, "bar")
