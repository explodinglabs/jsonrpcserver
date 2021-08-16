> :warning: **August 16, 2021: Version 5 released!** [Read about the
> changes](https://blog.explodinglabs.com/jsonrpcserver-5-changes), or jump to
> the [full documenation for version
> 5](https://www.jsonrpcserver.com/en/stable/).

# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver/week)
![Coverage Status](https://coveralls.io/repos/github/explodinglabs/jsonrpcserver/badge.svg?branch=master)

```python
from jsonrpcserver import Success, method, serve

@method
def ping():
    return Success("pong")

if __name__ == "__main__":
    serve()
```

Full documentation is at [jsonrpcserver.com](https://www.jsonrpcserver.com/).

See also: [jsonrpcclient](https://github.com/explodinglabs/jsonrpcclient)
