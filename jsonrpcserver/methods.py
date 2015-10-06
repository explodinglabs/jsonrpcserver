"""
methods.py

Methods add() syntax::

    >>> methods = Methods()
    >>> methods.add(lambda x: x * x, 'square')

Methods decorator syntax::

    >>> @methods.add
    ... def square(x):
    ...    return x * x
"""

from .exceptions import MethodNotFound


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
    This class makes it easy to build a list of methods to pass to dispatch().
    """

    def __init__(self):
        self._methods = []

    def __iter__(self):
        for method in self._methods:
            yield method

    def add(self, func, name=None):
        """
        Add a method to the list.
        """
        # Set the custom name on the function object.
        if name:
            func.__name__ = name
        if not hasattr(func, '__name__'):
            raise TypeError()
        self._methods.append(func)
        return func
