## How to disable schema validation?

Validating requests is costly - roughly 40% of dispatching time is spent on schema validation.
If you know the incoming requests are valid, you can disable the validation for better
performance.

```python
dispatch(request, validator=lambda _: None)
```

## Which HTTP status code to respond with?

I suggest:

```python
200 if response else 204
```

If the request was a notification, `dispatch` will give you an empty string. So
since there's no http body, use status code 204 - no content.

## How to rename a method

Use `@method(name="new_name")`.

Or use the dispatch function's [methods
parameter](https://www.jsonrpcserver.com/en/latest/dispatch.html#methods).

## How to get the response in other forms?

Instead of `dispatch`, use:

- `dispatch_to_serializable` to get the response as a dict.
- `dispatch_to_response` to get the response as a namedtuple (either a
  `SuccessResponse` or `ErrorResponse`, these are defined in
  [response.py](https://github.com/explodinglabs/jsonrpcserver/blob/main/jsonrpcserver/response.py)).

For these functions, if the request was a batch, you'll get a list of
responses. If the request was a notification, you'll get `None`.
