"""AioZMQ server"""
import asyncio

import aiozmq  # type: ignore
import zmq
from jsonrpcserver import async_dispatch, async_method, Ok, Result


@async_method
async def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


async def main() -> None:
    """Handle AioZMQ request"""
    rep = await aiozmq.create_zmq_stream(zmq.REP, bind="tcp://*:5000")
    while True:
        request = (await rep.read())[0].decode()
        if response := (await async_dispatch(request)).encode():
            rep.write((response,))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(aiozmq.ZmqEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())
