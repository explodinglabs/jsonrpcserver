import asyncio

from jsonrpcserver import method, Success, Result, async_dispatch
from websockets.server import WebSocketServerProtocol, serve


@method
async def ping() -> Result:
    return Success("pong")


async def main(websocket: WebSocketServerProtocol, path: str) -> None:
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
