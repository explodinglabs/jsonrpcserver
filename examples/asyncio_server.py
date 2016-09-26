import asyncio
from jsonrpcserver import Methods
from jsonrpcserver.async_dispatcher import dispatch

methods = Methods()

@methods.add
async def ping():
    return 'pong'

async def handle(request):
    return await dispatch(methods, request)

if __name__ == '__main__':
    request = '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
    response = asyncio.get_event_loop().run_until_complete(handle(request))
    print(str(response))
