import asyncio

from jsonrpcserver import async_dispatch, async_method, Ok, Result
import websockets


@async_method
async def ping() -> Result:
    return Ok("pong")


async def main(websocket, path):
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = websockets.serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
