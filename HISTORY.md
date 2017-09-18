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
