from jsonrpcserver.methods import global_methods, method


def test_decorator():
    @method
    def foo():
        pass

    assert callable(global_methods["foo"])


def test_decorator_custom_name():
    @method(name="baz")
    def bar():
        pass

    assert callable(global_methods["baz"])
