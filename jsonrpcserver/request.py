"""A simple namedtuple to hold a request.

After parsing the request string, we put the requests (which are dicts) into these
Request namedtuples because they're nicer to work with.
"""
from typing import Any, Dict, List, NamedTuple, Union


class Request(NamedTuple):
    method: str
    params: Union[List[Any], Dict[str, Any]]
    id: Any  # Use NOID for a Notification.
