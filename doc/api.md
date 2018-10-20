<p class="rubric"><a class="reference internal" href="index.html"><span class="doc">jsonrpcserver</span></a></p>

# jsonrpcserver Guide

Jsonrpcserver allows you to act on remote procedure calls.

## Installation

Install the package with pip:

```sh
pip install jsonrpcserver
```

For Python versions older than 3.6, install a 3.x version, and jump over to
[the 3.x docs](https://jsonrpcserver.readthedocs.io/en/3.5.6/).

```sh
pip install "jsonrpcserver>=3,<4"
```

There are three public functions, `method`, `serve` and `dispatch`.

## Methods

Use the `@method` decorator to register functions that can be called remotely:

```python
from jsonrpcserver import method, dispatch, serve

@method
def ping():
    return 'pong'
```

Methods can take either positional or named arguments (but not both, this is a
limitation of JSON-RPC).

## Serve

Start the development server:

```python
>>> serve()
 * Listening on port 5000
```

For production, use a more sophisticated framework (see [examples in various
frameworks](examples.html)). For those, there's a `dispatch` function.

## Dispatch

The `dispatch` function processes a JSON-RPC request and calls the appropriate
method:

```python
response = dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
```

The return value is a `Response` object.

Use `str()` to get the JSON-serialized response:

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

Other options can be passed to `dispatch`, or put in a config file (see
below):

**basic_logging**

Adds log handlers, to log all requests and responses to stderr.

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
convert_camel_case = yes
debug = yes
trim_log_values = yes
```

## Validation

Assert on arguments to validate them.

```python
@method
def fruits(color):
    assert color in ("red", "orange", "yellow"), "No fruits of that colour"
```

The dispatcher will give the appropriate response:

```python
>>> response = dispatch('{"jsonrpc": "2.0", "method": "fruits", "params": ["blue"], "id": 1}')
>>> str(response)
{'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': 1}
```

*To include the "No fruits of that colour" message in the response, pass
debug=True to dispatch.*

## Async

Asyncio is supported, allowing requests to be dispatched to coroutines.

```python
from jsonrpcserver import method, async_dispatch

@method
async def ping():
    return await some_long_running_task()

response = await async_dispatch(request)
```

Questions? [beauinmelbourne@gmail.com](mailto:beauinmelbourne@gmail.com)
or create an [issue](https://github.com/bcb/jsonrpcclient/issues).
