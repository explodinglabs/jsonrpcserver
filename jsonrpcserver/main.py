import json
import os
from configparser import ConfigParser
from typing import Any, Callable, Iterable, Union

from apply_defaults import apply_config  # type: ignore
from jsonschema.validators import validator_for  # type: ignore
from pkg_resources import resource_string  # type: ignore

from .dispatcher import dispatch_to_response_pure
from .methods import Methods, global_methods
from .response import Response, to_serializable
from .utils import compose, identity


default_deserializer = json.loads

# Prepare the jsonschema validator. This is global so it loads only once, not every
# time dispatch is called.
schema = json.loads(resource_string(__name__, "request-schema.json"))
klass = validator_for(schema)
klass.check_schema(schema)
default_schema_validator = klass(schema).validate

# Read configuration file
config = ConfigParser(default_section="dispatch")
config.read([".jsonrpcserverrc", os.path.expanduser("~/.jsonrpcserverrc")])


@apply_config(config)
def dispatch_to_response(
    request: str,
    methods: Methods = None,
    *,
    context: Any = None,
    schema_validator: Callable = default_schema_validator,
    deserializer: Callable = default_deserializer,
    post_process: Callable = identity,
) -> Union[Response, Iterable[Response], None]:
    """Dispatch a JSON-serialized request to methods.

    Maps a request string to a Response (or list of Responses).

    This is a public method which wraps dispatch_to_response_pure, adding default values
    and globals.

    Args:
        request: The JSON-RPC request string.
        methods: Collection of methods that can be called. If not passed, uses the
            internal, global methods object which is populated with the @method
            decorator.
        context: Will be passed to methods as the first param if not None.
        schema_validator: Function that validates the JSON-RPC request.
        deserializer: Function that deserializes the JSON-RPC request.

    Returns:
        A Response, list of Responses or None.

    Examples:
        >>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}', [ping])
    """
    return dispatch_to_response_pure(
        deserializer=deserializer,
        schema_validator=schema_validator,
        post_process=post_process,
        context=context,
        methods=global_methods if methods is None else methods,
        request=request,
    )


def dispatch_to_serializable(*args: Any, **kwargs: Any) -> Union[dict, list, None]:
    return dispatch_to_response(*args, post_process=to_serializable, **kwargs)


def dispatch_to_json(
    *args: Any, serializer: Callable = json.dumps, **kwargs: Any
) -> str:
    """This is the main public method, it goes through the entire JSON-RPC process,
    taking a JSON-RPC request string, dispatching it, converting the Response(s) into a
    serializable value and then serializing that to return a JSON-RPC response string.
    """
    return dispatch_to_response(
        *args, post_process=compose(serializer, to_serializable), **kwargs
    )


# "dispatch" is an alias of dispatch_to_json.
dispatch = dispatch_to_json
