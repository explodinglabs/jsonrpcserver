Async dispatch is supported.

```python
from jsonrpcserver import async_dispatch, async_method, Ok, Result

@async_method
async def ping() -> Result:
    return Ok("pong")

await async_dispatch('{"jsonrpc": "2.0", "method": "ping", "id": 1}')
```

Some reasons to use this:

- Use it with an asynchronous protocol like sockets or message queues.
- `await` long-running functions from your method.
- Batch requests are dispatched concurrently.

## Notifications

Notifications are requests without an `id`. We should not respond to
notifications, so jsonrpcserver gives an empty string to signify there is *no
response*.

```python
>>> await async_dispatch('{"jsonrpc": "2.0", "method": "ping"}')
''
```

If the response is an empty string, don't send it.

```python
if response := dispatch(request):
    send(response)
```

```{note}
A synchronous protocol like HTTP requires a response no matter what, so we can
send back the empty string. However with async protocols, we have the choice of
responding or not.
```
