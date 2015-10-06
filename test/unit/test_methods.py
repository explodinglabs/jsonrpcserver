"""test_methods.py"""
#pylint:disable=missing-docstring

from unittest import TestCase, main
from functools import partial

from jsonrpcserver.methods import Methods, _get_method
from jsonrpcserver.exceptions import MethodNotFound


class TestGetMethod(TestCase):

    def test_plain_list(self):
        def meow(): pass # pylint:disable=multiple-statements
        def woof(): pass # pylint:disable=multiple-statements
        self.assertIs(meow, _get_method([meow, woof], 'meow'))
        self.assertIs(woof, _get_method([meow, woof], 'woof'))

    def test_methods_object(self):
        def meow(): pass # pylint:disable=multiple-statements
        def woof(): pass # pylint:disable=multiple-statements
        methods = Methods()
        methods.add(meow)
        methods.add(woof)
        self.assertIs(meow, _get_method(methods, 'meow'))
        self.assertIs(woof, _get_method(methods, 'woof'))


class TestAdd(TestCase):

    def test_function(self):
        def go(): pass # pylint:disable=multiple-statements
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
        methods.add(add) # Lambda's __name__ will be '<lambda>', not 'add'
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
        with self.assertRaises(TypeError):
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


class TestDecorator(TestCase):

    def test_function(self):
        methods = Methods()
        @methods.add
        def go(): pass # pylint:disable=multiple-statements
        self.assertIs(go, _get_method(methods, 'go'))


if __name__ == '__main__':
    main()
