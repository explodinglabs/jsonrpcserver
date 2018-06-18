![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

```sh
pip install jsonrpcserver
```

```python
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'

if __name__ == '__main__':
    methods.serve_forever()
```

Full documentation is at [jsonrpcserver.readthedocs.io](https://jsonrpcserver.readthedocs.io/).

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
