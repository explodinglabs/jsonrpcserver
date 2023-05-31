"""Jsonrpcserver server.

Uses jsonrpcserver's built-in "serve" function.
"""
from jsonrpcserver import method, serve, Ok, Result


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


if __name__ == "__main__":
    serve()
