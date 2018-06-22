<p class="rubric"><a class="reference internal" href="index.html"><span class="doc">jsonrpcserver</span></a></p>

# jsonrpcserver Guide

This library allows you to act on remote procedure calls.

## Methods

First build a list of methods that can be called remotely.

Use the `methods.add` decorator to register a method to the list:

```python
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'
```

Add as many methods as needed, then serve the methods:

```python
>>> methods.serve_forever()
 * Listening on port 5000
```

The built-in `serve_forever()` method is a cheap-and-nasty way of taking
requests; ultimately you should use a more sophisticated server library (see
[examples in various frameworks](examples.html)).

For those, there's a `dispatch()` method.

## Dispatch

The dispatch function processes a JSON-RPC request and calls the appropriate
method:

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

There's also an HTTP status code if needed:

```python
>>> response.http_status
200
```

### Context

If you need to pass some extra data to the methods, such as configuration
settings, or the request object from the server framework, there's a `context`
param:

```python
methods.dispatch(request, context={'feature_enabled': True})
```

The methods should receive this value (it must be named `context`):

```python
@methods.add
def ping(context):
    ...
```

### Configuration

The following other options can be passed to `dispatch`

**convert_camel_case**

Attempts to clean up requests before processing, by changing the method and
parameter names to snake case. Default is *False*.

**debug**

If True, more information is included in error responses, such as an exception
message. Default is *False*.

**notification_errors**

Notifications are not responded to in almost all cases, however if you prefer,
notifications can receive error responses. Default is *False*.

**schema_validation**

Allows you to disable the validation of requests against the JSON-RPC schema.
Default is *True*.

## Validation

Methods can take arguments, positional or named (but not both, this is a
limitation of JSON-RPC).

If an argument is unsatisfactory, raise `InvalidParams`:

```python
from jsonrpcserver.exceptions import InvalidParams

@methods.add
def get_customer(**kwargs):
    if 'name' not in kwargs:
        raise InvalidParams('Name is required')
```

The dispatcher will catch the exception and give the appropriate response:

```python
>>> methods.dispatch({'jsonrpc': '2.0', 'method': 'get', 'params': {}, 'id': 1})
{'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}
```

*To include the "Name is required" message in the response, pass debug=True to
dispatch.*

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

## Disable logging

To disable the log entries:

```python
import logging
logging.getLogger("jsonrpcserver.dispatcher.request").setLevel(logging.WARNING)
logging.getLogger("jsonrpcserver.dispatcher.response").setLevel(logging.WARNING)
```

## Exceptions

See the list of exceptions raised by jsonrpcserver [here](exceptions.html).
