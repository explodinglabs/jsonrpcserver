"""test_methods.py"""
# pylint: disable=missing-docstring

from unittest import TestCase, main
from functools import partial

from jsonrpcserver.methods import Methods


class TestAdd(TestCase):

    def test_non_callable(self):
        m = Methods()
        with self.assertRaises(TypeError):
            m.add(None, 'ping')

    def test_function(self):
        def go(): pass # pylint: disable=multiple-statements
        m = Methods()
        m.add(go)
        self.assertIs(go, m['go'])

    def test_function_custom_name(self):
        def go(): pass # pylint:disable=multiple-statements
        m = Methods()
        m.add(go, 'go_now')
        self.assertIs(go, m['go_now'])

    def test_lambda_no_name(self):
        add = lambda x, y: x + y
        m = Methods()
        m.add(add) # Lambda's __name__ will be '<lambda>'!
        self.assertNotIn('add', m)

    def test_lambda_renamed(self):
        add = lambda x, y: x + y
        add.__name__ = 'add'
        m = Methods()
        m.add(add)
        self.assertIs(add, m['add'])

    def test_lambda_custom_name(self):
        add = lambda x, y: x + y
        m = Methods()
        m.add(add, 'add')
        self.assertIs(add, m['add'])

    def test_partial_no_name(self):
        six = partial(lambda x: x + 1, 5)
        m = Methods()
        with self.assertRaises(AttributeError):
            m.add(six) # Partial has no __name__ !

    def test_partial_renamed(self):
        six = partial(lambda x: x + 1, 5)
        six.__name__ = 'six'
        m = Methods()
        m.add(six)
        self.assertIs(six, m['six'])

    def test_partial_custom_name(self):
        six = partial(lambda x: x + 1, 5)
        m = Methods()
        m.add(six, 'six')
        self.assertIs(six, m['six'])

    def test_static_method(self):
        class FooClass(object):
            @staticmethod
            def Foo():
                return 'bar'
        m = Methods()
        m.add(FooClass.Foo)
        self.assertIs(FooClass.Foo, m['Foo'])

    def test_static_method_custom_name(self):
        class FooClass(object):
            @staticmethod
            def Foo():
                return 'bar'
        m = Methods()
        m.add(FooClass.Foo, 'custom')
        self.assertIs(FooClass.Foo, m['custom'])

    def test_instance_method(self):
        class FooClass(object):
            def Foo(self): # pylint: disable=no-self-use
                return 'bar'
        m = Methods()
        m.add(FooClass().Foo)
        self.assertEqual('bar', m['Foo'].__call__())

    def test_instance_method_custom_name(self):
        class Foo(object):
            def __init__(self, name):
                self.name = name
            def get_name(self):
                return self.name
        obj1 = Foo('a')
        obj2 = Foo('b')
        m = Methods()
        m.add(obj1.get_name, 'custom1')
        m.add(obj2.get_name, 'custom2')
        # Can't use assertIs, so check the outcome is as expected
        self.assertEqual('a', m['custom1'].__call__())
        self.assertEqual('b', m['custom2'].__call__())


class TestAddDictLike(TestCase):

    def test_function(self):
        m = Methods()
        def ping():
            return 'pong'
        m['ping'] = ping
        self.assertTrue(callable(m['ping']))

    def test_lambda(self):
        m = Methods()
        m['ping'] = lambda: 'pong'
        self.assertTrue(callable(m['ping']))

    def test_non_callable(self):
        m = Methods()
        with self.assertRaises(TypeError):
            m['ping'] = 1


class TestDecorator(TestCase):

    def test_function(self):
        m = Methods()
        @m.add
        def go(): pass # pylint:disable=multiple-statements
        self.assertIs(go, m['go'])

    def test_static_method(self):
        m = Methods()
        class FooClass(object):
            @staticmethod
            @m.add
            def Foo():
                return 'bar'
        self.assertIs(FooClass.Foo, m['Foo'])


if __name__ == '__main__':
    main()
