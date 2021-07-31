"""Demonstrates processing a batch of 100 requests asynchronously"""
import asyncio
import json

from jsonrpcserver import Success, method, async_dispatch as dispatch


@method
async def sleep_():
    await asyncio.sleep(1)
    return Success()


async def handle(request: str) -> None:
    print(await dispatch(request))


if __name__ == "__main__":
    request = json.dumps(
        [{"jsonrpc": "2.0", "method": "sleep_", "id": 1} for _ in range(100)]
    )
    asyncio.get_event_loop().run_until_complete(handle(request))
