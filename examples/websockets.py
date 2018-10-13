import asyncio
import websockets
from jsonrpcserver import method, async_dispatch as dispatch


@method
async def ping():
    return "pong"


async def main(websocket, path):
    response = await dispatch(await websocket.recv())
    if response.wanted:
        await websocket.send(str(response))


start_server = websockets.serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
