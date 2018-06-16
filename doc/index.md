# jsonrpcserver

Process [JSON-RPC](http://www.jsonrpc.org/) requests in Python 2.7 and 3.3+.

```python
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'

if __name__ == '__main__':
    methods.serve_forever()
```

Start the server:

```sh
$ pip install jsonrpcserver
$ python server.py
 * Listening on port 5000
```

This example uses the built-in server, but any application can process requests
with the `dispatch()` method. See [examples in various
frameworks](examples.html), or read the [guide to usage and
configuration](api.html).

Contribute on [Github](https://github.com/bcb/jsonrpcserver).

See also: [jsonrpcclient](https://jsonrpcclient.readthedocs.io/)
