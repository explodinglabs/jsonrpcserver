<p align="center">
  <img alt="Logo" height="96" src="https://github.com/explodinglabs/jsonrpcserver/blob/main/docs/logo.png?raw=true" />
</p>

<p align="center">
  <i>Process incoming JSON-RPC requests in Python</i>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/jsonrpcserver.svg" alt="PyPI" />
  <img src="https://github.com/explodinglabs/jsonrpcserver/actions/workflows/code-quality.yml/badge.svg" alt="Code Quality" />
  <img src="https://coveralls.io/repos/github/explodinglabs/jsonrpcserver/badge.svg?branch=main" alt="Coverage Status" />
  <img src="https://img.shields.io/pypi/dw/jsonrpcserver" alt="Downloads" />
  <img src="https://img.shields.io/pypi/l/jsonrpcserver.svg" alt="License" />
</p>

## Installation

```sh
pip install jsonrpcserver
```

## Usage

```python
from jsonrpcserver import dispatch, method, Success

@method
def ping():
    return Success("pong")

response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
# => '{"jsonrpc": "2.0", "result": "pong", "id": 1}'
```

Full documentation is at [jsonrpcserver.com](https://www.jsonrpcserver.com/).

## 📖 See Also

- [jsonrpcclient](https://github.com/explodinglabs/jsonrpcclient)
