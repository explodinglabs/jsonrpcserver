"""
Methods
*******

This module can be used to easily build a list of methods.

Create a Methods object and add methods to it::

    from jsonrpcserver import Methods
    methods = Methods()
    methods.add(cat)
    methods.add(dog)

Then pass it to ``dispatch()`` as you would a regular list::

    dispatch(methods, ...)
"""

from jsonrpcserver.exceptions import MethodNotFound


def _get_method(methods, name):
    """
    Finds a method in a list.
    :param methods: List of named functions.
    :param name: Method to find.
    :raises MethodNotFound: If the method wasn't in the list.
    :returns: The method from the list.
    """
    try:
        return next(m for m in methods if m.__name__ == name)
    except StopIteration:
        raise MethodNotFound(name)


class Methods(object):
    """Holds a list of methods."""

    def __init__(self):
        self._methods = []

    def __iter__(self):
        for method in self._methods:
            yield method

    def add(self, method, name=None):
        """
        Add a method to the list.

        To add a function::

            def cat():
                return 'meow'

            methods.add(cat)

        Alternatively, use the decorator::

            @methods.add
            def cat():
                return 'meow'

        Use a different name by giving a second argument::

            methods.add(cat, 'say_meow')

        Lambdas::

            methods.add(lambda: 'meow', 'cat')
            methods.add(lambda: 'woof', 'dog')

        Partials::

            multiply = lambda x, y: x * y
            methods.add(partial(multiply, 2), 'double')
            methods.add(partial(multiply, 3), 'triple')

        :param method: The method to add.
        :param name: Name of the method (optional).
        :raise TypeError: Raised if the method being added has no name. i.e. The
                          method has no ``__name__`` property, and no ``name``
                          argument was given.
        """
        # Set the custom name on the method.
        if name:
            method.__name__ = name
        if not hasattr(method, '__name__'):
            raise TypeError()
        self._methods.append(method)
        return method
