<p class="rubric"><a class="reference internal" href="index.html"><span class="doc">jsonrpcserver</span></a></p>

# jsonrpcserver Guide

This library allows you to act on remote procedure calls.

## Methods

First build a list of methods that can be called remotely.

Use the `@method` decorator to register a method to the list:

```python
from jsonrpcserver import method, serve

@method
def ping():
    return 'pong'
```

Add as many methods as needed, then start the development server:

```python
>>> serve()
 * Listening on port 5000
```

For production use a more sophisticated option (see [examples in various
frameworks](examples.html)).

For those, there's a `dispatch()` method.

## Dispatch

The `dispatch` function processes a JSON-RPC request and calls the appropriate
method:

```python
>>> response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
```

The return value is a `Response` object.

```python
>>> response.result
'pong'
```

Use `str()` to get a JSON-encoded string:

```python
>>> str(response)
'{"jsonrpc": "2.0", "result": "pong", "id": 1}'
```

There's also an HTTP status code if needed:

```python
>>> response.http_status
200
```

### Context

If you need to pass some extra data to the methods, such as configuration
settings, or the request object from the server framework, pass a `context`
object:

```python
dispatch(request, context={'feature_enabled': True})
```

The methods will receive this as the first positional param:

```python
@method
def ping(context):
    ...
```

### Configuration

Any of the following options can be passed to `dispatch`, or put in a config
file (see below):

**basic_logging**

Adds log handlers to log requests and responses to stderr.

**convert_camel_case**

Attempts to clean up requests before processing, by changing the method and
parameter names to snake case. Default is *False*.

**debug**

If True, more information is included in error responses, such as an exception
message. Default is *False*.

**trim_log_values**

Show abbreviated requests and responses in logs. Default is *False*.

### Config file

Here's an example of the config file `.jsonrpcclientrc` - this should be
placed in the current or home directory:

```ini
[general]
basic_logging = yes
```

## Validation

Methods can take arguments, positional or named (but not both, this is a
limitation of JSON-RPC).

Assert on arguments to validate them.

```python
@method
def fruits(color):
    assert color in ("red", "orange", "yellow"), "No fruits of that colour"
```

The dispatcher will give the appropriate response:

```python
>>> response = dispatch({'jsonrpc': '2.0', 'method': 'fruits', 'params': ["blue"], 'id': 1})
>>> response.deserialized()
{'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}
```

*To include the "Name is required" message in the response, pass debug=True to
dispatch.*

## Async

Asyncio is supported Python 3.5+, allowing requests to be dispatched to
coroutines.

```python
from jsonrpcserver import method, async_dispatch

@method
async def ping():
    return await some_long_running_task()

response = await async_dispatch(request)
```
