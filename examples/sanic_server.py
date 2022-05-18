from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from jsonrpcserver import dispatch_to_serializable, method, Ok, Result

app = Sanic("JSON-RPC app")


@method
def ping() -> Result:
    return Ok("pong")


@app.route("/", methods=["POST"])
async def test(request: Request):
    return json(dispatch_to_serializable(request.body))


if __name__ == "__main__":
    app.run(port=5000)
