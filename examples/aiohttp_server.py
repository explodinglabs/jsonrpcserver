from aiohttp import web
from jsonrpcserver import Methods, dispatch

methods = Methods()
@methods.add
def ping():
    return 'pong'

async def handle(request):
    request = await request.text()
    response = dispatch(methods, request)
    return web.json_response(response)

app = web.Application()
app.router.add_post('/', handle)

if __name__ == '__main__':
    web.run_app(app, port=5000)
