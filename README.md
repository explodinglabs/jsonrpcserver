![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

# jsonrpcserver

*Sep 17, 2018: Work on version 4 is underway, will be ready within a few
weeks.*

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

```python
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'

if __name__ == '__main__':
    methods.serve_forever()
```

Full documentation is at [jsonrpcserver.readthedocs.io](https://jsonrpcserver.readthedocs.io/).

## Testing

```sh
pip install pytest
pytest
```

See also: [jsonrpcclient](https://github.com/bcb/jsonrpcclient)
