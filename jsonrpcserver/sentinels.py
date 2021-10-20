"""Sentinels - these are used to indicate no data is present.

We can't use None, because None may be a valid piece of data.
"""

import sys


class Sentinel:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"<{sys.intern(str(self.name)).rsplit('.', 1)[-1]}>"


NOCONTEXT = Sentinel("NoContext")
NODATA = Sentinel("NoData")
NOID = Sentinel("NoId")
