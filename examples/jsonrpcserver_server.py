"""Jsonrpcserver server.

Uses jsonrpcserver's built-in "serve" function.
"""
from jsonrpcserver import method, Result, Success, serve


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


if __name__ == "__main__":
    serve()
