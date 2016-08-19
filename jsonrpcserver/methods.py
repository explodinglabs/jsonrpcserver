"""The methods passed to :func:`~dispatcher.dispatch` can be list of functions
like ``[speak, eat]``, a dictionary, or a ``Methods`` object::

    from jsonrpcserver import Methods
    methods = Methods()

    @methods.add
    def ping():
        return 'pong'

    methods.serve_forever()
"""
try:
    # Python 2
    from collections import MutableMapping
except ImportError:
    # Python 3
    from collections.abc import MutableMapping
from jsonrpcserver.http_server import MethodsServer


class Methods(MutableMapping, MethodsServer):
    """Holds a list of methods
    ... versionchanged:: 3.3
        Subclass MutableMapping instead of dict.
    """

    def __init__(self, *args, **kwargs):
        self._items = {}
        self.update(*args, **kwargs)

    def __repr__(self):
        return str(self._items)

    def __getitem__(self, key):
        return self._items[key]

    def __setitem__(self, key, value):
        # Method must be callable
        if not callable(value):
            raise TypeError('%s is not callable' % type(value))
        self._items[key] = value

    def __delitem__(self, key):
        del self._items[key]

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

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
            name = method.__name__
        # Method must have a name
        if not name:
            raise AttributeError('%s has no name' % type(method))
        self.update({name: method})
        return method

    def add_method(self, *args, **kwargs):
        """
        ... deprecated:: 3.2.3
            Use add instead.
        """
        return self.add(*args, **kwargs)
