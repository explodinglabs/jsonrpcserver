"""AioHTTP server"""

from aiohttp import web

from jsonrpcserver import Ok, Result, async_dispatch, async_method


@async_method
async def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


async def handle(request: web.Request) -> web.Response:
    """Handle aiohttp request"""
    return web.Response(
        text=await async_dispatch(await request.text()), content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, port=5000)
