"""FastAPI server"""
from fastapi import FastAPI, Request, Response
from jsonrpcserver import dispatch, method, Ok, Result
import uvicorn  # type: ignore

app = FastAPI()


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


@app.post("/")
async def index(request: Request) -> Response:
    """Handle FastAPI request"""
    return Response(dispatch(await request.body()))


if __name__ == "__main__":
    uvicorn.run(app, port=5000)
