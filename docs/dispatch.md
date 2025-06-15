# Dispatch

The `dispatch` function takes a JSON-RPC request, calls the appropriate method
and gives a JSON-RPC response.

```python
>>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
'{"jsonrpc": "2.0", "result": "pong", "id": 1}'
```

[See how dispatch is used in different frameworks.](examples.md)

## Optional parameters

### methods

This lets you specify a group of methods to dispatch to. It's an alternative to
using the `@method` decorator. The value should be a dict mapping function
names to functions.

```python
def ping():
    return Success("pong")

dispatch(request, methods={"ping": ping})
```

Default is `global_methods`, which is an internal dict populated by the
`@method` decorator.

### context

If specified, this will be the first argument to all methods.

```python
@method
def greet(context, name):
    return Success(context + " " + name)

>>> dispatch('{"jsonrpc": "2.0", "method": "greet", "params": ["Beau"], "id": 1}', context="Hello")
'{"jsonrpc": "2.0", "result": "Hello Beau", "id": 1}'
```

### deserializer

A function that parses the request string. Default is `json.loads`.

```python
dispatch(request, deserializer=ujson.loads)
```

### serializer

A function that serializes the response string. Default is `json.dumps`.

```python
dispatch(request, serializer=ujson.dumps)
```

### validator

A function that validates the request once the json has been parsed.
The function should raise an exception (any exception) if the request
doesn't match the JSON-RPC spec. Default is `default_validator` which
validates the request against a schema.
