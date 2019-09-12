# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

```python
from jsonrpcserver import method, serve

@method
def ping():
    return "pong"

if __name__ == "__main__":
    serve()
```

Full documentation is at [jsonrpcserver.readthedocs.io](https://jsonrpcserver.readthedocs.io/).

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
