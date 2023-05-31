"""Websockets server"""
import asyncio

from websockets.server import WebSocketServerProtocol, serve
from jsonrpcserver import async_dispatch, async_method, Ok, Result


@async_method
async def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


async def main(websocket: WebSocketServerProtocol, _: str) -> None:
    """Handle Websocket message"""
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
