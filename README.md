<p align="center">
  <img alt="Logo" height="96" src="https://github.com/explodinglabs/jsonrpcserver/blob/main/docs/logo.png?raw=true" />
</p>

<p align="center">
![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Code Quality](https://github.com/explodinglabs/jsonrpcserver/actions/workflows/code-quality.yml/badge.svg)
![Coverage Status](https://coveralls.io/repos/github/explodinglabs/jsonrpcserver/badge.svg?branch=main)
![Downloads](https://img.shields.io/pypi/dw/jsonrpcserver)
![License](https://img.shields.io/pypi/l/jsonrpcserver.svg)
</p>

<p align="center">
  <i>Process incoming JSON-RPC requests in Python</i>
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
