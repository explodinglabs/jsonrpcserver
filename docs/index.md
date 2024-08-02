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
$ pip install jsonrpcserver
$ python server.py
 * Listening on port 5000
```

Test the server:

```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
{"jsonrpc": "2.0", "result": "pong", "id": 1}
```

`serve` is good for serving methods in development, but for production use
`dispatch` instead.
