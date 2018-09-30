from aiohttp import web
from jsonrpcserver.aio import method, dispatch

@method
async def ping():
    return 'pong'

async def handle(request):
    request = await request.text()
    response = await dispatch(request)
    if response.wanted:
        return web.json_response(response, status=response.http_status)
    else:
        return web.Response()

app = web.Application()
app.router.add_post('/', handle)

if __name__ == '__main__':
    web.run_app(app, port=5000)
