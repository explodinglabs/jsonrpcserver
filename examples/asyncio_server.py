import asyncio
from jsonrpcserver.aio import methods

@methods.add
async def sleep():
    await asyncio.sleep(1)

async def handle(request):
    return await methods.dispatch(request)

if __name__ == '__main__':
    request = [
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'},
        {'jsonrpc': '2.0', 'method': 'sleep'}
    ]
    coro = handle(request)
    asyncio.get_event_loop().run_until_complete(coro)
