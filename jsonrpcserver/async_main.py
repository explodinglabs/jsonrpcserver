"""The public async api functions."""
import json
from typing import Any, Callable, Dict, Iterable, List, Optional, Union, cast

from apply_defaults import apply_config

from .async_dispatcher import dispatch_to_response_pure
from .dispatcher import Deserialized
from .main import config, default_schema_validator, default_deserializer
from .methods import Methods, global_methods
from .response import Response, to_serializable
from .sentinels import NOCONTEXT
from .utils import identity


@apply_config(config)
async def dispatch_to_response(
    request: str,
    methods: Optional[Methods] = None,
    *,
    context: Any = NOCONTEXT,
    deserializer: Callable[[str], Deserialized] = default_deserializer,
    schema_validator: Callable[[Deserialized], Deserialized] = default_schema_validator,
    post_process: Callable[[Deserialized], Iterable[Any]] = identity,
) -> Union[Response, Iterable[Response], None]:
    return await dispatch_to_response_pure(
        deserializer=deserializer,
        schema_validator=schema_validator,
        post_process=post_process,
        context=context,
        methods=global_methods if methods is None else methods,
        request=request,
    )


async def dispatch_to_serializable(
    *args: Any, **kwargs: Any
) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
    return cast(
        Union[Dict[str, Any], List[Dict[str, Any]], None],
        await dispatch_to_response(*args, post_process=to_serializable, **kwargs),
    )


async def dispatch_to_json(
    *args: Any,
    serializer: Callable[
        [Union[Dict[str, Any], List[Dict[str, Any]], None]], str
    ] = json.dumps,
    **kwargs: Any,
) -> str:
    response = await dispatch_to_serializable(*args, **kwargs)
    return "" if response is None else serializer(response)


# "dispatch" is an alias of dispatch_to_json.
dispatch = dispatch_to_json
