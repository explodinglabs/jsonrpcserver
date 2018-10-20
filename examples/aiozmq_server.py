import asyncio
import aiozmq
import zmq
from jsonrpcserver import method, async_dispatch as dispatch


@method
async def ping():
    return "pong"


async def main():
    rep = await aiozmq.create_zmq_stream(zmq.REP, bind="tcp://*:5000")
    while True:
        request = await rep.read()
        response = await dispatch(request[0].decode())
        rep.write((str(response).encode(),))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(aiozmq.ZmqEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())
