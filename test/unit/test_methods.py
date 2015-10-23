"""test_methods.py"""
#pylint:disable=missing-docstring

from unittest import TestCase, main
from functools import partial

from jsonrpcserver.methods import Methods, _get_method
from jsonrpcserver.exceptions import MethodNotFound


class TestGetMethod(TestCase):

    def test_list(self):
        def cat(): pass # pylint: disable=multiple-statements
        def dog(): pass # pylint: disable=multiple-statements
        self.assertIs(cat, _get_method([cat, dog], 'cat'))
        self.assertIs(dog, _get_method([cat, dog], 'dog'))

    def test_list_non_existant(self):
        def cat(): pass # pylint: disable=multiple-statements
        with self.assertRaises(MethodNotFound):
            _get_method([cat], 'cat_says')

    def test_dict(self):
        def cat(): pass # pylint: disable=multiple-statements
        def dog(): pass # pylint: disable=multiple-statements
        d = {'cat_says': cat, 'dog_says': dog}
        self.assertIs(cat, _get_method(d, 'cat_says'))
        self.assertIs(dog, _get_method(d, 'dog_says'))

    def test_dict_non_existant(self):
        def cat(): pass # pylint: disable=multiple-statements
        with self.assertRaises(MethodNotFound):
            _get_method({'cat_says': cat}, 'cat')

    def test_methods_object(self):
        def cat(): pass # pylint: disable=multiple-statements
        def dog(): pass # pylint: disable=multiple-statements
        methods = Methods()
        methods.add(cat)
        methods.add(dog)
        self.assertIs(cat, _get_method(methods, 'cat'))
        self.assertIs(dog, _get_method(methods, 'dog'))


class TestAdd(TestCase):

    def test_function(self):
        def go(): pass # pylint: disable=multiple-statements
        methods = Methods()
        methods.add(go)
        self.assertIs(go, _get_method(methods, 'go'))

    def test_function_custom_name(self):
        def go(): pass # pylint:disable=multiple-statements
        methods = Methods()
        methods.add(go, 'go_now')
        self.assertIs(go, _get_method(methods, 'go_now'))

    def test_lambda_no_name(self):
        add = lambda x, y: x + y
        methods = Methods()
        methods.add(add) # Lambda's __name__ will be '<lambda>'!
        with self.assertRaises(MethodNotFound):
            _get_method(methods, 'add')

    def test_lambda_renamed(self):
        add = lambda x, y: x + y
        add.__name__ = 'add'
        methods = Methods()
        methods.add(add)
        self.assertIs(add, _get_method(methods, 'add'))

    def test_lambda_custom_name(self):
        add = lambda x, y: x + y
        methods = Methods()
        methods.add(add, 'add')
        self.assertIs(add, _get_method(methods, 'add'))

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
        self.assertIs(six, _get_method(methods, 'six'))

    def test_partial_custom_name(self):
        six = partial(lambda x: x + 1, 5)
        methods = Methods()
        methods.add(six, 'six')
        self.assertIs(six, _get_method(methods, 'six'))

    def test_static_method(self):
        class FooClass(object):
            @staticmethod
            def Foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.Foo)
        self.assertIs(FooClass.Foo, _get_method(methods, 'Foo'))

    def test_static_method_custom_name(self):
        class FooClass(object):
            @staticmethod
            def Foo():
                return 'bar'
        methods = Methods()
        methods.add(FooClass.Foo, 'custom')
        self.assertIs(FooClass.Foo, _get_method(methods, 'custom'))

    def test_instance_method(self):
        class FooClass(object):
            def Foo(self): # pylint: disable=no-self-use
                return 'bar'
        methods = Methods()
        methods.add(FooClass().Foo)
        self.assertEqual('bar', _get_method(methods, 'Foo').__call__())

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
        self.assertEqual('a', _get_method(methods, 'custom1').__call__())
        self.assertEqual('b', _get_method(methods, 'custom2').__call__())


class TestDecorator(TestCase):

    def test_function(self):
        methods = Methods()
        @methods.add
        def go(): pass # pylint:disable=multiple-statements
        self.assertIs(go, _get_method(methods, 'go'))

    def test_static_method(self):
        methods = Methods()
        class FooClass(object):
            @staticmethod
            @methods.add
            def Foo():
                return 'bar'
        self.assertIs(FooClass.Foo, _get_method(methods, 'Foo'))


if __name__ == '__main__':
    main()
