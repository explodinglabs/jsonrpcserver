> :warning: **Note: This master branch is for development of the upcoming version 5**, which is [currently in beta](https://github.com/bcb/jsonrpcserver/discussions/204). For the latest stable version, see the [4.x branch](https://github.com/bcb/jsonrpcserver/tree/4.x). Also, please pin your dependency to "jsonrpcserver<5" until you're ready to upgrade to v5.

# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

```python
from jsonrpcserver import Success, method, serve

@method
def ping():
    return Success("pong")

if __name__ == "__main__":
    serve()
```

Full documentation is at [jsonrpcserver.com](https://www.jsonrpcserver.com/).

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
