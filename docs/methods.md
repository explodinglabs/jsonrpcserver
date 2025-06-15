# Methods

Methods are functions that can be called by a JSON-RPC request. To write one,
decorate a function with `@method`:

```python
from jsonrpcserver import method, Result, Success, Error

@method
def ping() -> Result:
    return Success("pong")
```

If you don't need to respond with any value simply `return Success()`.

## Responses

Methods return either `Success` or `Error`. These are the [JSON-RPC response
objects](https://www.jsonrpc.org/specification#response_object) (excluding the
`jsonrpc` and `id` parts). `Error` takes a code, message, and optionally 'data'.

```python
@method
def test() -> Result:
    return Error(1, "There was a problem")
```

> 📝 Alternatively, raise a `JsonRpcError`, which takes the same
> arguments as `Error`.

## Parameters

Methods can accept arguments.

```python
@method
def hello(name: str) -> Result:
    return Success("Hello " + name)
```

Testing it:

```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "hello", "params": ["Beau"], "id": 1}'
{"jsonrpc": "2.0", "result": "Hello Beau", "id": 1}
```

## Invalid params

A common error response is _invalid params_. The JSON-RPC error code
for this is **-32602**. A shortcut, _InvalidParams_, is included so
you don't need to remember that.

```python
from jsonrpcserver import method, Result, InvalidParams, Success, dispatch

@method
def within_range(num: int) -> Result:
    if num not in range(1, 5):
        return InvalidParams("Value must be 1-5")
    return Success()
```

This is the same as saying

```python
return Error(-32602, "Invalid params", "Value must be 1-5")
```
