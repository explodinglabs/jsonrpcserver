Methods are functions that can be called by a JSON-RPC request. To write one,
decorate a function with `@method`:

```python
from jsonrpcserver import method, Error, Ok, Result

@method
def ping() -> Result:
    return Ok("pong")
```

If you don't need to respond with any value simply `return Ok()`.

## Responses

Methods return either `Ok` or `Error`. These are the [JSON-RPC response
objects](https://www.jsonrpc.org/specification#response_object) (excluding the
`jsonrpc` and `id` parts). `Error` takes a code, message, and optionally
'data'.

```python
@method
def test() -> Result:
    return Error(1, "There was a problem")
```

```{note}
Alternatively, raise a `JsonRpcError`, which takes the same arguments as `Error`.
```

## Parameters

Methods can accept arguments.

```python
@method
def hello(name: str) -> Result:
    return Ok("Hello " + name)
```

Testing it:

```sh
$ curl -X POST http://localhost:5000 -d '{"jsonrpc": "2.0", "method": "hello", "params": ["Beau"], "id": 1}'
{"jsonrpc": "2.0", "result": "Hello Beau", "id": 1}
```

## Invalid params

A common error response is *invalid params*.
The JSON-RPC error code for this is **-32602**. A shortcut, *InvalidParams*, is
included so you don't need to remember that.

```python
from jsonrpcserver import dispatch, method, InvalidParams, Ok, Result

@method
def within_range(num: int) -> Result:
    if num not in range(1, 5):
        return InvalidParams("Value must be 1-5")
    return Ok()
```

This is the same as saying
```python
return Error(-32602, "Invalid params", "Value must be 1-5")
```
