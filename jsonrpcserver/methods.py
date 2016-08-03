""":func:`~dispatcher.dispatch` takes a ``list`` of functions, but it can also
take a ``Methods`` object::

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add
    def cube(**kwargs):
        return kwargs['num']**3

    dispatch(methods, ...)
"""
class Methods(dict):
    """Holds a list of methods"""

    def add(self, method, name=None):
        """Add a method to the list::

            methods.add(cube)

        Alternatively, use as a decorator::

            @methods.add
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
                    'Use add(method, name) to specify a method name'
                    % type(method))
            name = method.__name__
        self[name] = method
        return method
