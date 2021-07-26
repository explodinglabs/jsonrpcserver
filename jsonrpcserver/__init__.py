"""We alias the imports so mypy considers them re-exported."""

from .async_main import (
    dispatch as async_dispatch,
    dispatch_to_response as async_dispatch_to_response,
    dispatch_to_serializable as async_dispatch_to_serializable,
)
from .main import (
    dispatch as dispatch,
    dispatch_to_response as dispatch_to_response,
    dispatch_to_serializable as dispatch_to_serializable,
)
from .methods import method
from .result import (
    Error as Error,
    InvalidParams as InvalidParams,
    Result as Result,
    Success as Success,
)
from .server import serve as serve
