"""test_methods.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main
from functools import partial

from jsonrpcserver.methods import Methods
from jsonrpcserver.exceptions import MethodNotFound


class TestAdd(TestCase):

    def test_function(self):
        def go(): pass # pylint: disable=multiple-statements
        methods = Methods()
        methods.add(go)
        self.assertIs(go, methods['go'])

    def test_function_custom_name(self):
        def go(): pass # pylint:disable=multiple-statements
        methods = Methods()
        methods.add(go, 'go_now')
        self.assertIs(go, methods['go_now'])

    def test_lambda_no_name(self):
        add = lambda x, y: x + y
        methods = Methods()
        methods.add(add) # Lambda's __name__ will be '<lambda>'!
        with self.assertRaises(KeyError):
            methods['add']

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
            def Foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.Foo)
        self.assertIs(FooClass.Foo, methods['Foo'])

    def test_static_method_custom_name(self):
        class FooClass(object):
            @staticmethod
            def Foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.Foo, 'custom')
        self.assertIs(FooClass.Foo, methods['custom'])

    def test_instance_method(self):
        class FooClass(object):
            def Foo(self): # pylint: disable=no-self-use
                return 'bar'
        methods = Methods()
        methods.add(FooClass().Foo)
        self.assertEqual('bar', methods['Foo'].__call__())

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


class TestDecorator(TestCase):

    def test_function(self):
        methods = Methods()
        @methods.add
        def go(): pass # pylint:disable=multiple-statements
        self.assertIs(go, methods['go'])

    def test_static_method(self):
        methods = Methods()
        class FooClass(object):
            @staticmethod
            @methods.add
            def Foo():
                return 'bar'
        self.assertIs(FooClass.Foo, methods['Foo'])


if __name__ == '__main__':
    main()
