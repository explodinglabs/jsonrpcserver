---
hide:
  - title
  - toc
---

# Installation

Create a `server.py`:

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
$ pip install jsonrpcserver
$ python server.py
 * Listening on port 5000
```

Test the server:

```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
{"jsonrpc": "2.0", "result": "pong", "id": 1}
```
