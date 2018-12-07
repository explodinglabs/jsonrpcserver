# Jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

*Version 4 is out. It's Python 3.6+ only. See the
[changelog](https://github.com/bcb/jsonrpcserver/blob/master/CHANGELOG.md),
[example usage](https://jsonrpcserver.readthedocs.io/en/latest/examples.html),
and read the [updated documentation](https://jsonrpcserver.readthedocs.io/).*

```python
from jsonrpcserver import method, serve

@method
def ping():
    return "pong"

if __name__ == "__main__":
    serve()
```

Full documentation is at [jsonrpcserver.readthedocs.io](https://jsonrpcserver.readthedocs.io/).

## Testing

```sh
pip install pytest mypy
pytest
mypy jsonrpcserver
```

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
