from jsonrpcserver.methods import global_methods, method


def test_decorator() -> None:
    @method
    def foo() -> None:
        pass

    assert callable(global_methods["foo"])


def test_decorator_custom_name() -> None:
    @method(name="baz")
    def bar() -> None:
        pass

    assert callable(global_methods["baz"])
