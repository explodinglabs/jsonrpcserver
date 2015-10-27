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
    """Finds a method in a list (or dictionary).

    :param methods: List or dictionary of named functions.
    :param name: Name of the method to find.
    :raises MethodNotFound: If the method wasn't in the list.
    :returns: The method from the list.
    """
    # If it's a dictionary, search for the key
    if isinstance(methods, dict):
        try:
            return methods[name]
        except KeyError:
            raise MethodNotFound(name)
    # Otherwise it must be a list, search the __name__ attributes
    try:
        return next(m for m in methods if m.__name__ == name)
    except StopIteration:
        raise MethodNotFound(name)


class Methods(dict):
    """Holds a dict of methods."""

    def __getitem__(self, key):
        return self.__dict__[key]

    def add(self, method, name=None):
        """Add a method to the list.

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
        :raise AttributeError: Raised if the method being added has no name.
                               i.e. The method has no ``__name__`` property, and
                               no ``name`` argument was given.
        """
        # If no custom name was given, use the method's __name__ attribute
        if not name:
            if not hasattr(method, '__name__'):
                raise AttributeError(
                    '%s has no __name__ attribute. '
                    'Use add(method, name) to specify a method name'
                    % type(method))
            name = method.__name__
        self.__dict__[name] = method
        return method
