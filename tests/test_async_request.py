import inspect, asyncio
from unittest import TestCase, main

from jsonrpcserver.aio import methods
from jsonrpcserver.async_request import AsyncRequest


def async_test(f):
    def wrapper(*args, **kwargs):
        if inspect.iscoroutinefunction(f):
            future = f(*args, **kwargs)
        else:
            coroutine = asyncio.coroutine(f)
            future = coroutine(*args, **kwargs)
        asyncio.get_event_loop().run_until_complete(future)
    return wrapper


class MyMethods():
    async def foo(self):
        return 'bar'

methods.add(MyMethods().foo)

class TestCall(TestCase):
    @async_test
    async def test_request(self):
        req = AsyncRequest({'jsonrpc': '2.0', 'method': 'foo', 'id': 1})
        response = await req.call(methods)
        self.assertEqual('bar', response['result'])

if __name__ == '__main__':
    main()
