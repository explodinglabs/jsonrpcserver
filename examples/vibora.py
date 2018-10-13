from vibora import Vibora, Request
from vibora.responses import JsonResponse
from jsonrpcserver import method, async_dispatch as dispatch

app = Vibora()


@method
async def ping():
    return "pong"


@app.route("/", methods=["POST"])
async def home(request: Request):
    request = await request.stream.read()
    response = await dispatch(request.decode())
    return JsonResponse(response.deserialized())



if __name__ == "__main__":
    app.run()
