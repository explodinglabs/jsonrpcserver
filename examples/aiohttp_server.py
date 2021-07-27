from aiohttp import web
from jsonrpcserver import Success, async_dispatch, method


@method
async def ping():
    return Success("pong")


async def handle(request):
    return web.json_response(await async_dispatch(await request.text()))


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, port=5000)
