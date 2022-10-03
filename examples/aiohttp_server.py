"""AioHTTP server"""
from aiohttp import web  # type: ignore
from jsonrpcserver import method, Result, Success, async_dispatch


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


async def handle(request: web.Request) -> web.Response:
    """Handle aiohttp request"""
    return web.Response(
        text=await async_dispatch(await request.text()), content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, port=5000)
