> :warning: August 16, 2021: Version 5 has been released. [Read about the
> changes](https://blog.explodinglabs.com/jsonrpcserver-5-changes), or jump to
> the [full documenation for version
> 5](https://www.jsonrpcserver.com/en/stable/). Development of version 4 has
> moved to the [4.x
> branch](https://github.com/explodinglabs/jsonrpcserver/tree/4.x).

# jsonrpcserver

Process incoming JSON-RPC requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver/week)
![Checks](https://github.com/explodinglabs/jsonrpcserver/actions/workflows/checks.yml/badge.svg)
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

See also: [jsonrpcclient](https://www.jsonrpcclient.com/)
