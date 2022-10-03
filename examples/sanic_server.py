"""Sanic server"""
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, json
from jsonrpcserver import Result, Success, dispatch_to_serializable, method

app = Sanic("JSON-RPC app")


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@app.route("/", methods=["POST"])
async def test(request: Request) -> HTTPResponse:
    """Handle Sanic request"""
    return json(dispatch_to_serializable(request.body))


if __name__ == "__main__":
    app.run(port=5000)
