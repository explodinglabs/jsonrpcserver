import asyncio
from jsonrpcserver.aio import methods

@methods.add
async def sleep_():
    await asyncio.sleep(1)

async def handle(request):
    return await methods.dispatch(request)

if __name__ == '__main__':
    request = [{'jsonrpc': '2.0', 'method': 'sleep_'} for _ in range(100)]
    asyncio.get_event_loop().run_until_complete(handle(request))
