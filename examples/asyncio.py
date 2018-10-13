"""Demonstrates processing a batch of 100 requests asynchronously"""
import asyncio
from json import dumps as serialize
from jsonrpcserver import method, async_dispatch as dispatch

@method
async def sleep_():
    await asyncio.sleep(1)

async def handle(request):
    return await dispatch(request)

if __name__ == '__main__':
    request = serialize([{"jsonrpc": "2.0", "method": "sleep_"} for _ in range(100)])
    asyncio.get_event_loop().run_until_complete(handle(request))
