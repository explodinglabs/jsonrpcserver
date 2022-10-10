"""Test methods.py"""
from jsonrpcserver import Result
from jsonrpcserver.methods import global_methods, method

# pylint: disable=missing-function-docstring

# pylint: disable=missing-function-docstring


def test_decorator() -> None:
    @method
    def func() -> Result:
        pass

    assert callable(global_methods["func"])


def test_decorator_custom_name() -> None:
    @method(name="new_name")
    def name() -> None:
        pass

    assert callable(global_methods["new_name"])
