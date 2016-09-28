import asyncio
import websockets
from jsonrpcserver.aio import methods

@methods.add
async def ping():
    return 'pong'

async def main(websocket, path):
    request = await websocket.recv()
    response = await methods.dispatch(request)
    await websocket.send(str(response))

start_server = websockets.serve(main, 'localhost', 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
