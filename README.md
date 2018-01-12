![Coverage Status](https://coveralls.io/repos/github/bcb/jsonrpcserver/badge.svg?branch=master)

# jsonrpcserver

[![Join the chat at https://gitter.im/jsonrpcserver/Lobby](https://badges.gitter.im/jsonrpcserver/Lobby.svg)](https://gitter.im/jsonrpcserver/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python 2.7 and 3.3+.

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
