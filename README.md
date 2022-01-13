> August 16, 2021: Version 5 has been released. Read about the [changes in
> version 5](https://composed.blog/jsonrpcserver-5-changes). 

<img
    alt="jsonrpcserver"
    style="margin: 0 auto;"
    src="https://github.com/explodinglabs/jsonrpcserver/blob/main/docs/logo.png?raw=true"
/>

Process incoming JSON-RPC requests in Python.

![PyPI](https://img.shields.io/pypi/v/jsonrpcserver.svg)
![Code Quality](https://github.com/explodinglabs/jsonrpcserver/actions/workflows/code-quality.yml/badge.svg)
![Coverage Status](https://coveralls.io/repos/github/explodinglabs/jsonrpcserver/badge.svg?branch=main)
![Downloads](https://img.shields.io/pypi/dm/jsonrpcserver.svg)

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
