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
pip install "jsonrpcserver<4"
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

Methods can accept either positional or named arguments (but not both -- this
is a limitation of JSON-RPC).

The RPC method will have the same name as the Python function; to use a
different name, pass it to the decorator, for example `@method(name="foo")`.

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

`deserialized()` gives the response as a Python object:

```python
>>> response.deserialized()
{'jsonrpc': '2.0', 'result': 'pong', 'id': 1}
```

There's also an HTTP status code if needed:

```python
>>> response.http_status
200
```

To use a custom serializer or deserializer, pass them to dispatch:

```python
response = dispatch(request, serialize=ujson.dumps, deserialize=ujson.loads)
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

**trim_log_values**

Show abbreviated requests and responses in logs. Default is *False*.

### Config file

Here's an example of the config file `.jsonrpcclientrc` - this should be
placed in the current or home directory:

```ini
[general]
basic_logging = yes
trim_log_values = yes
```

## Errors

The library handles some errors related to the JSON-RPC standard, such as
invalid json or invalid json-rpc requests.

To return a custom error response:

```python
from jsonrpcserver.dispatcher import Context
from jsonrpcserver.response import InvalidParamsResponse, Response, SuccessResponse
)

@method
def fruits(context: Context, color: str) -> Response:
    if color not in ["red", "orange", "yellow"]:
        return InvalidParamsResponse("No fruits of that colour", id=context.request.id)
    return SuccessResponse("blue", id=context.request.id)
```

The dispatcher will give the appropriate response:

```python
>>> dispatch('{"jsonrpc": "2.0", "method": "fruits", "params": {"color": "blue"}, "id": 1}')
InvalidParamsResponse(code=-32602, message='Invalid parameters', id=1)
```

To send some other application-defined error response, return an
`ApiErrorResponse` in a similar way.

```python
from jsonrpcserver.response import ApiErrorResponse

@method
def my_method():
    if some_condition:
        return ApiErrorResponse("Can't fulfill the request")
```

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
