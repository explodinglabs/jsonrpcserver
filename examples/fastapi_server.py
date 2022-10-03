"""FastAPI server"""
from fastapi import FastAPI, Request, Response
import uvicorn  # type: ignore
from jsonrpcserver import Result, Success, dispatch, method

app = FastAPI()


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@app.post("/")
async def index(request: Request) -> Response:
    """Handle FastAPI request"""
    return Response(dispatch(await request.body()))


if __name__ == "__main__":
    uvicorn.run(app, port=5000)
