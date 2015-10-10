"""
Methods
*******

To make it easier to build the list of methods, a Methods class is provided::

    >>> from jsonrpcserver import Methods
    >>> methods = Methods()

Add methods to it with `methods.add() <#methods.Methods.add>`_.

Pass the Methods object to ``dispatch()`` as you would a regular list::

    >>> dispatch(methods, ...)
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
    """
    Easy way to build a list of methods.
    """

    def __init__(self):
        self._methods = []

    def __iter__(self):
        for method in self._methods:
            yield method

    def add(self, func, name=None):
        """
        Add a method to the list.

        Example, adding a function::

            def cat():
                return 'meow'
            methods.add(cat)

        Alternatively, use the decorator::

            @methods.add
            def cat():
                return 'meow'

        Adding lambdas (note that I can easily *name* the lambda in the second
        parameter)::

            methods.add(lambda: 'meow', 'cat')
            methods.add(lambda: 'woof', 'dog')

        Adding partials::

            multiply = lambda x, y: x * y
            methods.add(partial(multiply, 2), 'double')
            methods.add(partial(multiply, 3), 'triple')

        :param func: The function, lambda or partial to add.
        :param name: Name of the method (optional). Useful for lambdas and
                     partials.
        :raise TypeError: If the method being added has no name. (It has no
                          ``__name__`` property, and none is specified in the
                          ``name`` argument.)

        """
        # Set the custom name on the function object.
        if name:
            func.__name__ = name
        if not hasattr(func, '__name__'):
            raise TypeError()
        self._methods.append(func)
        return func
