The `dispatch` function takes a JSON-RPC request, attempts to call a method and gives a
JSON-RPC response.

```python
>>> dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
'{"jsonrpc": "2.0", "result": "pong", "id": 1}'
```

[See how dispatch is used in different frameworks.](examples)

## Optional parameters

The `dispatch` function has some optional parameters that allow you to
customise how it works.

### methods

This lets you specify the methods to dispatch to. It's an alternative to using
the `@method` decorator. The value should be a dict mapping function names to
functions.

```python
def ping():
    return Ok("pong")

dispatch(request, methods={"ping": ping})
```

Default is `global_methods`, which is an internal dict populated by the
`@method` decorator.

### context

If specified, this will be the first argument to all methods.

```python
@method
def greet(context, name):
    return Ok(f"Hello {context}")

>>> dispatch('{"jsonrpc": "2.0", "method": "greet", "params": ["Beau"], "id": 1}', context="Beau")
'{"jsonrpc": "2.0", "result": "Hello Beau", "id": 1}'
```

### deserializer

A function that parses the JSON request string. Default is `json.loads`.

```python
dispatch(request, deserializer=ujson.loads)
```

### jsonrpc_validator

A function that validates the request once the JSON string has been parsed. The
function should raise an exception (any exception) if the request doesn't match
the JSON-RPC spec (https://www.jsonrpc.org/specification). Default is
`default_jsonrpc_validator` which uses Jsonschema to validate requests against
a schema.

To disable JSON-RPC validation, pass `jsonrpc_validator=lambda _: None`, which
will improve performance because this validation takes around half the dispatch
time.

### args_validator

A function that validates a request's parameters against the signature of the
Python function that will be called for it. Note this should not validate the
_values_ of the parameters, it should simply ensure the parameters match the
Python function's signature. For reference, see the `validate_args` function in
`dispatcher.py`, which is the default `args_validator`.

### serializer

A function that serializes the response string. Default is `json.dumps`.

```python
dispatch(request, serializer=ujson.dumps)
```
