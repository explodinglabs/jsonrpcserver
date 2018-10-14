"""
Request class.

Represents a JSON-RPC request object.
"""
import re
from typing import Any, Dict, List, Optional, Tuple, Union

NOCONTEXT = object()
NOPARAMS = object()


# NOID is used as a request's id attribute to signify request is a Notification. We
# can't use None which is a valid ID.
NOID = object()


def convert_camel_case_string(name: str) -> str:
    """Convert camel case string to snake case"""
    string = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", string).lower()


def convert_camel_case_keys(original_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Converts all keys of a dict from camel case to snake case, recursively"""
    new_dict = dict()
    for key, val in original_dict.items():
        if isinstance(val, dict):
            # Recurse
            new_dict[convert_camel_case_string(key)] = convert_camel_case_keys(val)
        else:
            new_dict[convert_camel_case_string(key)] = val
    return new_dict


def get_arguments(
    params: Union[List, Dict, object] = NOPARAMS, context: Any = NOCONTEXT
) -> Tuple[List, Dict]:
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
        context: Optionally include some context data, which will be included as the
            first positional arguments passed to the method.

    Returns:
        A two-tuple containing the positional (in a list, or None) and named (in a dict,
        or None) arguments, extracted from the 'params' part of the request.
    """
    positionals, nameds = [], {}  # type: list, dict
    if params is not NOPARAMS:
        assert isinstance(params, (list, dict))
        if isinstance(params, list):
            positionals, nameds = (params, {})
        elif isinstance(params, dict):
            positionals, nameds = ([], params)

    # If context data was passed, include it as the first positional argument.
    if context is not NOCONTEXT:
        positionals = [context] + positionals

    return (positionals, nameds)


class Request:
    """
    Represents a JSON-RPC Request object.

    Encapsulates a JSON-RPC request, providing details such as the method name,
    arguments, and whether it's a request or a notification, and provides a `process`
    method to execute the request.

    Note: There's no need to validate here, because the schema should have validated the
    data already.
    """

    def __init__(
        self,
        method: str,
        *,
        params: Any = None,
        id: Any = NOID,
        jsonrpc: Optional[str] = None,  # ignored
        context: Any = NOCONTEXT,
        convert_camel_case: bool = False,
    ) -> None:
        """
        Args:
            method, params, id, jsonrpc: Parts of the JSON-RPC request.
            context: If passed, will be the first positional argument passed to the
                method.
            convert_camel_case: Will convert the method name and any keyword parameter
                names to snake_case.
        """
        self.jsonrpc = jsonrpc
        self.method = method
        self.args, self.kwargs = (
            get_arguments(params, context=context)
            if isinstance(params, (list, dict))
            else ([], {})
        )
        self.id = id

        if convert_camel_case:
            self.method = convert_camel_case_string(self.method)
            if self.kwargs:
                self.kwargs = convert_camel_case_keys(self.kwargs)

    @property
    def is_notification(self) -> bool:
        """
        Returns:
            True if the request is a JSON-RPC Notification (ie. No id attribute is
            included). False if it doesn't, meaning it's a JSON-RPC "Request".
        """
        return self.id is NOID
