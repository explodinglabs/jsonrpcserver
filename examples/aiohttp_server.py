from aiohttp import web
from jsonrpcserver import methods, dispatch

app = web.Application()

@methods.add
def ping():
    return 'pong'

async def handle(request):
    request = await request.text()
    response = dispatch(methods, request)
    return web.json_response(response)

app.router.add_post('/', handle)

if __name__ == '__main__':
    web.run_app(app, port=5000)
