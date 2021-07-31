import asyncio
import websockets
from jsonrpcserver import Success, method, async_dispatch as dispatch


@method
async def ping():
    return Success("pong")


async def main(websocket, path):
    if response := await dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = websockets.serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
