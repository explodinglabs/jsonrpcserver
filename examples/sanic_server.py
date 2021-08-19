from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from jsonrpcserver import Result, Success, dispatch_to_serializable, method

app = Sanic("My Hello, world app")


@method
def ping() -> Result:
    return Success("pong")


@app.route("/", methods=["POST"])
async def test(request: Request):
    return json(dispatch_to_serializable(request.body))


if __name__ == "__main__":
    app.run(port=5000)
