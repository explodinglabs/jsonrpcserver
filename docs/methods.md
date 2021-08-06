# Methods

Methods are functions that can be called by a JSON-RPC request.

To write one, decorate a function with `@method`:

```python
from jsonrpcserver import method, Result, Success

@method
def ping() -> Result:
    return Success("pong")
```

## Responses

The return value from methods can be either `Success` or `Error`. These are the
[JSON-RPC response
objects](https://www.jsonrpc.org/specification#response_object) (minus the
`jsonrpc` and `id` parts, the library takes care of those for you).

`Success` can include a result value. `Error` needs a `code` and a `message`
(you may also include a third value, `data`).

```python
from jsonrpcserver import method, Result, Error

@method
def test() -> Result:
    return Error(1, "There was a problem")
```

Alternatively, raise a `JsonRpcError`, which takes the same arguments as `Error`.

## Parameters

Methods can accept arguments.

```python
@method
def hello(name: str) -> Result:
    return Success("Hello " + name)
```

Test it:

```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "hello", "params": ["Beau"], "id": 1}'
{"jsonrpc": "2.0", "result": "Hello Beau", "id": 1}
```

## Invalid params

Invalid params is a common error response. The JSON-RPC error code for invalid
params is **-32602**. A shortcut, *InvalidParams*, is included so you don't
need to remember it.

```python
from jsonrpcserver import method, Result, InvalidParams, Success

@method
def within_range(num: int) -> Result:
    if num not in range(1, 5):
        return InvalidParams("Value must be 1-5")
    return Success()
```

This is the same as using
```python
return Error(-32602, "Invalid params", "Value must be 1-5")
```
