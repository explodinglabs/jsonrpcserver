import json
import pkgutil
import re
try:
    # Python 2
    from collections import Mapping, Sequence
except ImportError:
    # Python 3
    from collections.abc import Mapping, Sequence

import jsonschema
from funcsigs import signature

from .exceptions import InvalidParams, InvalidRequest, MethodNotFound


_JSON_VALIDATOR = jsonschema.Draft4Validator(json.loads(pkgutil.get_data(
    __name__, 'request-schema.json').decode()))


def convert_camel_case(name):
    """Convert a camelCase string to under_score"""
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', string).lower()


def convert_camel_case_keys(original_dict):
    """Converts all keys of a dict from camelCase to under_score, recursively"""
    new_dict = dict()
    for key, val in original_dict.items():
        if isinstance(val, dict):
            # Recurse
            new_dict[convert_camel_case(key)] = convert_camel_case_keys(val)
        else:
            new_dict[convert_camel_case(key)] = val
    return new_dict


def validate_against_schema(request):
    """
    Validate the request against the JSON-RPC schema.

    :param request: JSON-RPC request (dictionary).
    :raises InvalidRequest: If the request is invalid.
    :returns: None
    """
    try:
        _JSON_VALIDATOR.validate(request)
    except jsonschema.ValidationError as exc:
        raise InvalidRequest(exc.message)


def validate_arguments_against_signature(func, args, kwargs):
    """
    Check if the request's arguments match a function's signature.

    Raises InvalidParams exception if arguments cannot be passed to a
    function.

    :param func: The function to check.
    :param args: Positional arguments.
    :param kwargs: Keyword arguments.
    :raises InvalidParams: If the arguments cannot be passed to the function.
    """
    try:
        signature(func).bind(*(args or []), **(kwargs or {}))
    except TypeError as exc:
        raise InvalidParams(str(exc))


def get_method(methods, name):
    """
    Find a method in a list (or dictionary).

    :param methods: List or dictionary of named functions.
    :param name: Name of the method to find.
    :raises MethodNotFound: If the method wasn't in the list.
    :returns: The method from the list.
    """
    # If it's a Mapping (dict-like), search for the key
    if isinstance(methods, Mapping):
        try:
            return methods[name]
        except KeyError:
            raise MethodNotFound(name)
    # Otherwise it must be a Sequence, search the __name__ attributes of
    # its items
    elif isinstance(methods, Sequence):
        try:
            return next(m for m in methods if m.__name__ == name)
        except StopIteration:
            raise MethodNotFound(name)


def get_arguments(params, context=None):
    """
    Get the positional and keyword arguments of a request.

    Takes the 'params' part of a JSON-RPC request and converts it to either
    positional or keyword arguments usable in a Python function call. Note that
    a JSON-RPC request can have positional or keyword arguments, but not both.
    See http://www.jsonrpc.org/specification#parameter_structures

    :param params: The 'params' part of the JSON-RPC request (should be a
        list or dict). The 'params' value can be a JSON array (Python list),
        object (Python dict), or None.
    :param context: Optionally include some context data, which will be included
        in the keyword arguments passed to the method.
    :raises InvalidParams: If 'params' was present but was not a list or
        dict.
    :returns: A two-tuple containing the positionals (in a list, or None) and
        keywords (in a dict, or None) extracted from the 'params' part of the
        request.
    """
    positionals = keywords = None
    if params:
        # Params is a list. Taken as positional arguments.
        if isinstance(params, list):
            positionals = params
        # Params is a dict. Taken as keyword arguments.
        elif isinstance(params, dict):
            keywords = params
        # Any other type is invalid. (This should never happen if the request
        # has passed the schema validation.)
        else:
            raise InvalidParams('Params of type %s is not allowed' % \
                type(params).__name__)
    # Can't have both positional and keyword arguments. It's impossible in json
    # anyway; the params arg can only be a json array (list) or object (dict)
    assert not (positionals and keywords), \
        'Cannot have both positional and keyword arguments in JSON-RPC.'
    # If context data was passed, include it as a keyword argument.
    if context is not None:
        keywords = {} if not keywords else keywords
        keywords['context'] = context
    return (positionals, keywords)
