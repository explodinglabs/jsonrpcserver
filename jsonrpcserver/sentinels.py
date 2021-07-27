import sys


class Sentinel:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"<{sys.intern(str(self.name)).rsplit('.', 1)[-1]}>"


NODATA = Sentinel("NoData")
NOCONTEXT = Sentinel("NoContext")
NOID = Sentinel("NoId")
