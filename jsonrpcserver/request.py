"""
Request class.

Represents a JSON-RPC request object.
"""
import logging
import re
import traceback
from typing import Any, Callable, Dict, List, Generator, Optional, Tuple, Union
from funcsigs import signature  # type: ignore

import jsonschema  # type: ignore

from .log import log
from .methods import Methods

UNSPECIFIED = object()
NOID = object()


def convert_camel_case_string(name: str) -> str:
    """Convert camel case string to snake case"""
    string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()


def convert_camel_case_keys(original_dict: 'Request') -> 'Request':
    """Converts all keys of a dict from camel case to snake case, recursively"""
    new_dict = dict()
    for key, val in original_dict.items():
        if isinstance(val, dict):
            # Recurse
            new_dict[convert_camel_case_string(key)] = convert_camel_case_keys(val)
        else:
            new_dict[convert_camel_case_string(key)] = val
    return new_dict


def validate_arguments_against_signature(
    func: Callable, args: Optional[Dict], kwargs: Optional[List]
) -> None:
    """
    Check if the request's arguments match a function's signature.

    Raises TypeError exception if arguments cannot be passed to a function.

    Args:
        func: The function to check.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Raises:
        TypeError: If the arguments cannot be passed to the function.
    """
    signature(func).bind(*(args or []), **(kwargs or {}))


def get_arguments(
    params: Union[List, Dict], context: Union[Dict, object] = UNSPECIFIED
) -> Tuple[Optional[List], Optional[Dict]]:
    """
    Get the positional and keyword arguments from a request.

    Takes the 'params' part of a JSON-RPC request and converts it to either positional
    or named arguments usable in a Python function call. Note that a JSON-RPC request
    can only have positional _or_ named arguments, but not both. See
    http://www.jsonrpc.org/specification#parameter_structures

    Args:
        params: The 'params' part of the JSON-RPC request (should be a list or dict).
            The 'params' value can be a JSON array (Python list), object (Python dict),
            or None.
        context: Optionally include some context data, which will be included in the
            keyword arguments passed to the method.

    Returns:
        A two-tuple containing the positional (in a list, or None) and named (in a dict,
        or None) arguments, extracted from the 'params' part of the request.

    Raises:
        TypeError: If 'params' was present but was not a list or dict.
        AssertionError: If both positional and names arguments specified, which is not
            allowed in JSON-RPC.
    """
    positionals = nameds = None
    if params:
        # Params is a list. Taken as positional arguments.
        if isinstance(params, list):
            positionals = params
        # Params is a dict. Taken as keyword arguments.
        elif isinstance(params, dict):
            nameds = params
        # Any other type is invalid. (This should never happen if the request
        # has passed the schema validation.)
        else:
            raise TypeError(
                "Params of type %s is not allowed" % type(params).__name__
            )
    # Can't have both positional and keyword arguments. It's impossible in json
    # anyway; the params arg can only be a json array (list) or object (dict)
    assert not (
        positionals and nameds
    ), "Cannot have both positional and keyword arguments in JSON-RPC."
    # If context data was passed, include it as a keyword argument.
    if context is not UNSPECIFIED:
        nameds = {} if not nameds else nameds
        nameds["context"] = context
    return (positionals, nameds)


class Request:
    """
    Represents a JSON-RPC Request object.

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a `process`
    method to execute the request.
    """

    def __init__(
        self,
        request: Dict[str, Any],
        context: Union[Dict, object] = UNSPECIFIED,
        convert_camel_case: bool = False,
    ) -> None:
        """
        Args:
            request: JSON-RPC request, deserialized into a dict.
            context: Optional context object that will be passed to the RPC method.
            convert_camel_case:
            schema_validation:
        """
        # Get method name and arguments
        self.method_name = request["method"]
        self.args, self.kwargs = get_arguments(request.get("params"), context=context)
        # We use NOID because None (null) is a valid request id
        self.request_id = request["id"] if "id" in request else NOID

        if convert_camel_case:
            self.method_name = convert_camel_case_string(self.method_name)
            if self.kwargs:
                self.kwargs = convert_camel_case_keys(self.kwargs)

    @property
    def is_notification(self) -> bool:
        """
        Returns:
            True if the request is a JSON-RPC Notification (ie. No id attribute is
            included). False if it doesn't, meaning it's a JSON-RPC "Request".
        """
        return self.request_id is NOID
