from fastapi import FastAPI, Request, Response
from jsonrpcserver import Result, Success, dispatch, method
import uvicorn

app = FastAPI()


@method
def ping() -> Result:
    return Success("pong")


@app.post("/")
async def index(request: Request):
    return Response(dispatch(await request.body()))


if __name__ == "__main__":
    uvicorn.run(app, port=5000)
