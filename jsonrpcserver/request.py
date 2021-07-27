from typing import Any, Dict, List, NamedTuple, Union


class Request(NamedTuple):
    method: str
    params: Union[List[Any], Dict[str, Any]]
    id: Any  # Use NOID for a Notification.
