"""test_methods.py"""
from functools import partial
from unittest import TestCase, main

from jsonrpcserver.methods import Methods


class TestInit(TestCase):
    def test_dict(self):
        methods = Methods({'ping': lambda: 'pong'})
        self.assertIn('ping', methods)

    def test_named_args(self):
        methods = Methods(ping=lambda: 'pong')
        self.assertIn('ping', methods)


class TestMutableMapping(TestCase):
    @staticmethod
    def test_iter():
        methods = Methods(ping=lambda: 'pong')
        iter(methods)

    def test_len(self):
        methods = Methods(ping=lambda: 'pong')
        self.assertEqual(1, len(methods))

    @staticmethod
    def test_del():
        methods = Methods(ping=lambda: 'pong')
        del methods['ping']


class TestAdd(TestCase):
    def test_non_callable(self):
        methods = Methods()
        with self.assertRaises(TypeError):
            methods.add(None, 'ping')

    def test_no_name(self):
        methods = Methods()
        with self.assertRaises(AttributeError):
            methods.add(None)

    def test_function(self):
        def foo(): pass
        methods = Methods()
        methods.add(foo)
        self.assertIs(foo, methods['foo'])

    def test_function_custom_name(self):
        def foo(): pass
        methods = Methods()
        methods.add(foo, 'foobar')
        self.assertIs(foo, methods['foobar'])

    def test_lambda_no_name(self):
        add = lambda x, y: x + y
        methods = Methods()
        methods.add(add) # Lambda's __name__ will be '<lambda>'!
        self.assertNotIn('add', methods)

    def test_lambda_renamed(self):
        add = lambda x, y: x + y
        add.__name__ = 'add'
        methods = Methods()
        methods.add(add)
        self.assertIs(add, methods['add'])

    def test_lambda_custom_name(self):
        add = lambda x, y: x + y
        methods = Methods()
        methods.add(add, 'add')
        self.assertIs(add, methods['add'])

    def test_partial_no_name(self):
        six = partial(lambda x: x + 1, 5)
        methods = Methods()
        with self.assertRaises(AttributeError):
            methods.add(six) # Partial has no __name__ !

    def test_partial_renamed(self):
        six = partial(lambda x: x + 1, 5)
        six.__name__ = 'six'
        methods = Methods()
        methods.add(six)
        self.assertIs(six, methods['six'])

    def test_partial_custom_name(self):
        six = partial(lambda x: x + 1, 5)
        methods = Methods()
        methods.add(six, 'six')
        self.assertIs(six, methods['six'])

    def test_static_method(self):
        class FooClass(object):
            @staticmethod
            def foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.foo)
        self.assertIs(FooClass.foo, methods['foo'])

    def test_static_method_custom_name(self):
        class FooClass(object):
            @staticmethod
            def foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.foo, 'custom')
        self.assertIs(FooClass.foo, methods['custom'])

    def test_instance_method(self):
        class FooClass(object):
            def foo(self):
                return 'bar'
        methods = Methods()
        methods.add(FooClass().foo)
        self.assertEqual('bar', methods['foo'].__call__())

    def test_instance_method_custom_name(self):
        class Foo(object):
            def __init__(self, name):
                self.name = name
            def get_name(self):
                return self.name
        obj1 = Foo('a')
        obj2 = Foo('b')
        methods = Methods()
        methods.add(obj1.get_name, 'custom1')
        methods.add(obj2.get_name, 'custom2')
        # Can't use assertIs, so check the outcome is as expected
        self.assertEqual('a', methods['custom1'].__call__())
        self.assertEqual('b', methods['custom2'].__call__())


class TestAddMethod(TestCase):
    """add_method is the old way to add, still need to support it"""
    def test(self):
        def foo(): pass
        methods = Methods()
        methods.add_method(foo)
        self.assertIs(foo, methods['foo'])


class TestAddDictLike(TestCase):
    def test_function(self):
        methods = Methods()
        def ping():
            return 'pong'
        methods['ping'] = ping
        self.assertTrue(callable(methods['ping']))

    def test_lambda(self):
        methods = Methods()
        methods['ping'] = lambda: 'pong'
        self.assertTrue(callable(methods['ping']))

    def test_non_callable(self):
        methods = Methods()
        with self.assertRaises(TypeError):
            methods['ping'] = 1


class TestDecorator(TestCase):
    def test_function(self):
        methods = Methods()
        @methods.add
        def foo(): pass
        self.assertIs(foo, methods['foo'])

    def test_static_method(self):
        methods = Methods()
        class FooClass(object):
            @staticmethod
            @methods.add
            def foo():
                return 'bar'
        self.assertIs(FooClass.foo, methods['foo'])


if __name__ == '__main__':
    main()
