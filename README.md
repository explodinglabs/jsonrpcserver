![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Downloads](https://pepy.tech/badge/jsonrpcserver)
![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

# jsonrpcserver

Oct 14, 2018: Version 4 release candidate is ready for testing! Try it with
`pip install jsonrpcserver==4.0.0-rc2`. See basic usage in the code branch
[here](https://github.com/bcb/jsonrpcserver/tree/4.0) or full documentation
[here](https://github.com/bcb/jsonrpcserver/blob/4.0/doc/api.md).

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
