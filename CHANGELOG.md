# jsonrpcserver Change Log

## 4.0.0 (Aug 27, 2018)
- The dispatch function now only takes a `Methods` object. No longer accepts a
  dictionary or list.
- No more exceptions. Calling code will _always_ get a valid JSON-RPC
  response from `dispatch`. The old `InvalidParamsException` is gone - instead
  return an `InvalidParamsResponse` if params are invalid.
- No more responding to notifications, even for errors. (except invalid
  json/json-rpc, in which case it's not possible to know if the request is a
  notification)
- response.is_notification is now is_request
- Add type hints
- Move all tests to pytest
- Removed the config module. Use params/configuration file.
- Methods class takes args & kwargs
- `response.is_notification` changed to `response.wanted`.

## 3.5.6 (Jun 28, 2018)
- Add trim_log_values dispatch param. (#65)
- Fix a missing import

## 3.5.5 (Jun 19, 2018)
- Rewrite of dispatch(), adding parameters to configure the dispatch that were
  previously configured by modifying the `config` module. That module is now
  deprecated and will be removed in 4.0.

## 3.5.4 (Apr 30, 2018)
- Refactoring

## 3.5.3 (Dec 19, 2017)
- Allow requests to have any non-None id

## 3.5.2 (Sep 19, 2017)
- Refactor for Request subclassing

## 3.5.1 (Aug 12, 2017)
- Include context data in regular (synchronous) methods.dispatch

## 3.5.0 (Aug 12, 2017)
- Pass some context data through dispatch to the methods.
- Fix not calling notifications in batch requests.

## 3.4.3 (Jul 13, 2017)
- Fix AttributeError on batch responses

## 3.4.3 (Jul 12, 2017)
- Add `Response.is_notification` attribute

## 3.4.2 (Jun 9, 2017)
- Fix `convert_camel_case` with array params

## 3.4.1 (Oct 4, 2016)
- Disable logging in config
- Performance improved
- Fix async batch requests

## 3.4.0 (Sep 27, 2016)
- Added asyncio support. (Python 3.5+)
- Added a *methods* object to the jsonrpcserver module (so you can import
  jsonrpcserver.methods, rather than instantiating your own).
- Added methods.dispatch().

## 3.3.4 (Sep 22, 2016)
- Fix Methods.serve_forever in python 2 (thanks @bplower)

## 3.3.3 (Sep 15, 2016)
- Updated method of logging exception (thanks @bplower)

## 3.3.2 (Aug 19, 2016)
- Pass Methods named args onto MutableMapping
- Remove unused logger

## 3.3.1 (Aug 5, 2016)
- Allow passing dict to Methods constructor

## 3.3.0 (Aug 5, 2016)
- A basic HTTP server has been added.
