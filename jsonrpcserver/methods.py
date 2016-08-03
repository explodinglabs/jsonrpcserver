""":func:`~dispatcher.dispatch` takes a ``list`` of functions, but you can also
give it a ``Methods`` object::

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add_method
    def cube(**kwargs):
        return kwargs['num']**3

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
    """Holds a list of methods"""

    def __getitem__(self, key):
        return self.__dict__[key]

    def add_method(self, method, name=None):
        """Add a method to the list::

            methods.add_method(cube)

        Alternatively, use as a decorator::

            @methods.add_method
            def cube(**kwargs):
                return kwargs['num']**3

        :param method: The method to add.
        :param name: Name of the method (optional).
        :raise AttributeError:
            Raised if the method being added has no name. (i.e. it has no
            ``__name__`` property, and no ``name`` argument was given.)
        """
        # If no custom name was given, use the method's __name__ attribute
        if not name:
            if not hasattr(method, '__name__'):
                raise AttributeError(
                    '%s has no __name__ attribute. '
                    'Use add_method(method, name) to specify a method name'
                    % type(method))
            name = method.__name__
        self.__dict__[name] = method
        return method
