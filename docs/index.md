# Jsonrpcserver

Jsonrpcserver processes JSON-RPC requests.

## Quickstart

Install jsonrpcserver:
```python
pip install jsonrpcserver
```

Create a `server.py`:

```python
from jsonrpcserver import method, serve, Ok

@method
def ping():
    return Ok("pong")

if __name__ == "__main__":
    serve()
```

Start the server:
```sh
$ python server.py
```

Send a request:
```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
{"jsonrpc": "2.0", "result": "pong", "id": 1}
```

`serve` starts a basic development server. Do not use it in a production deployment. Use
a production WSGI server instead, with jsonrpcserver's [dispatch](dispatch) function.
