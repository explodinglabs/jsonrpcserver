![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

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
pip install pytest
pytest
```

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
