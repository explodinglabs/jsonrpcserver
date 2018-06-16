<p class="rubric"><a class="reference internal" href="index.html"><span class="doc">jsonrpcserver</span></a></p>

# jsonrpcserver Guide

Showing how to use the [jsonrpcserver](https://github.com/bcb/jsonrpcserver) library.

## Methods

Build a list of methods that can be called remotely.

Use the `add` decorator to register a method to the list:

```python
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'
```

Add as many methods as needed.

Serve the methods:

```python
>>> methods.serve_forever()
 * Listening on port 5000
```

## Dispatching

Dispatch a JSON-RPC request:

```python
>>> response = methods.dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
--> {"jsonrpc": "2.0", "method": "ping", "id": 1}
<-- {"jsonrpc": "2.0", "result": "pong", "id": 1}
```

The return value is a `Response` object.

```python
>>> response
{'jsonrpc': '2.0', 'result': 'foo', 'id': 1}
```

Use `str()` to get a JSON-encoded string:

```python
>>> str(response)
'{"jsonrpc": "2.0", "result": "foo", "id": 1}'
```

There's also an HTTP status code if you need to respond to an HTTP request:

```python
>>> response.http_status
200
```

## Validation

If an argument is unsatisfactory, raise `InvalidParams`:

```python
from jsonrpcserver.exceptions import InvalidParams

@methods.add
def get_customer(**kwargs):
    if 'name' not in kwargs:
        raise InvalidParams('name is required')
```

The dispatcher catches the exception and gives the appropriate response:

```python
>>> methods.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {}, 'id': 1})
{'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}
```

*To include the "name is required" message given when the exception was raised,
enable debug mode (see Configuration).*

## Context

You may want the methods to receive some extra context data, such as
configuration or something from the web framework; for this use `context`:

```python
@methods.add
def ping(context):
    ...

methods.dispatch(request, context={'feature_enabled': True})
```

## Async

Asyncio is supported Python 3.5+, allowing requests to be dispatched to
coroutines.

Import methods from `jsonrpcserver.aio`:

```python
from jsonrpcserver.aio import methods

@methods.add
async def ping():
    return await some_long_running_task()
```

Then `await` the dispatch:

```python
response = await methods.dispatch(request)
```

## Configuration

Import this module to configure the library:

```python
from jsonrpcserver import config
config.debug = True
```

Other feature toggles include convert_camel_case, log_requests, log_responses,
notification_errors and schema_validation.

## Exceptions

See the [list of exceptions](exceptions.html) raised by jsonrpcserver.
