from vibora import Vibora, Request
from vibora.responses import JsonResponse
from jsonrpcserver.aio import methods

app = Vibora()

@methods.add
async def ping():
    return 'pong'

@app.route('/', methods=['POST'])
async def home(request: Request):
    response = await methods.dispatch(await request.json())
    return JsonResponse(response)

if __name__ == '__main__':
    app.run()
