# FAQ

## How to get the response in other forms

Todo

## How to disable the schema validation?

Roughly 40% of the time taken to dispatch is spent on schema validation. If you
trust the incoming requests are valid, you can disable the validation for
better performance.

```python
dispatch(request, validator=lambda _: None)
```

## How to get a HTTP status code to respond with?

Todo
