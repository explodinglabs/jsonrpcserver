from unittest import TestCase, main

from jsonrpcserver.exceptions import InvalidParams, MethodNotFound
from jsonrpcserver.methods import Methods
from jsonrpcserver.request_utils import *


# Some dummy functions to use for testing
def foo():
    return 'bar'

class FooClass():
    def foo(self, one, two):
        return 'bar'


class TestConvertCamelCase(TestCase):
    def test(self):
        self.assertEqual('foo_bar', convert_camel_case('fooBar'))


class TestConvertCamelCaseKeys(TestCase):
    def test(self):
        dictionary = {'fooKey': 1, 'aDict': {'fooKey': 1, 'barKey': 2}}
        self.assertEqual({'foo_key': 1, 'a_dict': {'foo_key': 1, 'bar_key': 2}}, \
                convert_camel_case_keys(dictionary))


class TestValidateArgumentsAgainstSignature(TestCase):
    """Keep it simple here. No need to test signature.bind."""
    @staticmethod
    def test_no_arguments():
        validate_arguments_against_signature(lambda: None, None, None)

    def test_no_arguments_too_many_positionals(self):
        with self.assertRaises(InvalidParams):
            validate_arguments_against_signature(lambda: None, ['foo'], None)

    @staticmethod
    def test_positionals():
        validate_arguments_against_signature(lambda x: None, [1], None)

    def test_positionals_not_passed(self):
        with self.assertRaises(InvalidParams):
            validate_arguments_against_signature(lambda x: None, None, {'foo': 'bar'})

    @staticmethod
    def test_keywords():
        validate_arguments_against_signature(lambda **kwargs: None, None, {'foo': 'bar'})

    @staticmethod
    def test_object_method():
        validate_arguments_against_signature(FooClass().foo, ['one', 'two'], None)


class TestGetMethod(TestCase):
    def test_list(self):
        def cat(): pass
        def dog(): pass
        self.assertIs(cat, get_method([cat, dog], 'cat'))
        self.assertIs(dog, get_method([cat, dog], 'dog'))

    def test_list_non_existant(self):
        def cat(): pass
        with self.assertRaises(MethodNotFound):
            get_method([cat], 'cat_says')

    def test_dict(self):
        def cat(): pass
        def dog(): pass
        dictionary = {'cat_says': cat, 'dog_says': dog}
        self.assertIs(cat, get_method(dictionary, 'cat_says'))
        self.assertIs(dog, get_method(dictionary, 'dog_says'))

    def test_dict_non_existant(self):
        def cat(): pass
        with self.assertRaises(MethodNotFound):
            get_method({'cat_says': cat}, 'cat')

    def test_methods_object(self):
        def cat(): pass
        def dog(): pass
        methods = Methods()
        methods.add(cat)
        methods.add(dog)
        self.assertIs(cat, get_method(methods, 'cat'))
        self.assertIs(dog, get_method(methods, 'dog'))


class TestGetArguments(TestCase):
    def test_none(self):
        self.assertEqual((None, None), get_arguments(None))

    def test_positional(self):
        self.assertEqual(([2, 3], None), get_arguments([2, 3]))

    def test_keyword(self):
        self.assertEqual((None, {'foo': 'bar'}), get_arguments({'foo': 'bar'}))

#    def test_invalid_none(self):
#        with self.assertRaises(InvalidParams):
#            get_arguments(None)

    def test_invalid_numeric(self):
        with self.assertRaises(InvalidParams):
            get_arguments(5)

    def test_invalid_string(self):
        with self.assertRaises(InvalidParams):
            get_arguments('str')

    # With the "context" argument
    def test_no_arguments_with_context(self):
        args = get_arguments(None, context='foo')
        self.assertEqual((None, {'context': 'foo'}), args)

    def test_positional_with_context(self):
        args = get_arguments(['foo'], context='bar')
        self.assertEqual((['foo'], {'context': 'bar'}), args)

    def test_keyword_with_context(self):
        args = get_arguments({'foo': 'bar'}, context='baz')
        self.assertEqual((None, {'foo': 'bar', 'context': 'baz'}), args)


if __name__ == '__main__':
    main()
