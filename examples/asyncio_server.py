"""Demonstrates processing a batch of 100 requests asynchronously with asyncio."""
import asyncio
import json

from jsonrpcserver import method, Result, Success, async_dispatch


@method
async def sleep_() -> Result:
    """JSON-RPC method"""
    await asyncio.sleep(1)
    return Success()


async def handle(req: str) -> None:
    """Handle asyncio event"""
    print(await async_dispatch(req))


if __name__ == "__main__":
    request = json.dumps(
        [{"jsonrpc": "2.0", "method": "sleep_", "id": 1} for _ in range(100)]
    )
    asyncio.get_event_loop().run_until_complete(handle(request))
