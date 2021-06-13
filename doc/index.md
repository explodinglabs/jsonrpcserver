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

Start the server:

```sh
$ pip install jsonrpcserver
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
