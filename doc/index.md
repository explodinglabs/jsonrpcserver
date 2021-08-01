# jsonrpcserver 5

> Version 5 is currently in beta. For the stable release go to [version
> 4](https://jsonrpcserver.com/en/stable/).

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python.

```python
from jsonrpcserver import Success, method, serve

@method
def ping():
    return Success("pong")

if __name__ == "__main__":
    serve()
```

Start the server:

```sh
$ pip install --pre jsonrpcserver
$ python server.py
 * Listening on port 5000
```

This example uses the built-in server, but any application can process
requests with the `dispatch()` method.

## Examples

See [examples in various frameworks](examples.html).

## Guide

Read the [guide to usage and configuration](api.html).

## Contribute

Contribute on [Github](https://github.com/bcb/jsonrpcserver).

## See Also

[jsonrpcclient](https://jsonrpcclient.readthedocs.io/)
