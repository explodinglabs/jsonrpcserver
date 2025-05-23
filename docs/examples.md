# Examples

## aiohttp

```python
from aiohttp import web

from jsonrpcserver import Result, Success, async_dispatch, method


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


async def handle(request: web.Request) -> web.Response:
    """Handle aiohttp request"""
    return web.Response(
        text=await async_dispatch(await request.text()), content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, port=5000)
```

See [blog post](https://explodinglabs.github.io/jsonrpc/aiohttp).

## Django

Create a `views.py`:

```python
from django.http import HttpRequest, HttpResponse  # type: ignore
from django.views.decorators.csrf import csrf_exempt  # type: ignore

from jsonrpcserver import Result, Success, dispatch, method


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@csrf_exempt  # type: ignore
def jsonrpc(request: HttpRequest) -> HttpResponse:
    """Handle Django request"""
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
```

See [blog post](https://explodinglabs.github.io/jsonrpc/django).

## FastAPI

```python
import uvicorn
from fastapi import FastAPI, Request, Response

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
```

See [blog post](https://explodinglabs.github.io/jsonrpc/fastapi).

## Flask

```python
from flask import Flask, Response, request

from jsonrpcserver import Result, Success, dispatch, method

app = Flask(__name__)


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@app.route("/", methods=["POST"])
def index() -> Response:
    """Handle Flask request"""
    return Response(
        dispatch(request.get_data().decode()), content_type="application/json"
    )


if __name__ == "__main__":
    app.run()
```

See [blog post](https://explodinglabs.github.io/jsonrpc/flask).

## http.server

Using Python's built-in
[http.server](https://docs.python.org/3/library/http.server.html) module.

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

from jsonrpcserver import Result, Success, dispatch, method


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


class TestHttpServer(BaseHTTPRequestHandler):
    """HTTPServer request handler"""

    def do_POST(self) -> None:  # pylint: disable=invalid-name
        """POST handler"""
        # Process request
        request = self.rfile.read(int(self.headers["Content-Length"])).decode()
        response = dispatch(request)
        # Return response
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())


if __name__ == "__main__":
    HTTPServer(("localhost", 5000), TestHttpServer).serve_forever()
```

See [blog post](https://explodinglabs.github.io/jsonrpc/httpserver).

## jsonrpcserver

Using jsonrpcserver's built-in `serve` method.

```python
from jsonrpcserver import Result, Success, method, serve


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


if __name__ == "__main__":
    serve()
```

## Sanic

```python
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
```

See [blog post](https://explodinglabs.github.io/jsonrpc/sanic).

## Socket.IO

```python
from flask import Flask, Request
from flask_socketio import SocketIO, send  # type: ignore

from jsonrpcserver import Result, Success, dispatch, method

app = Flask(__name__)
socketio = SocketIO(app)


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@socketio.on("message")  # type: ignore
def handle_message(request: Request) -> None:
    """Handle SocketIO request"""
    if response := dispatch(request):
        send(response, json=True)


if __name__ == "__main__":
    socketio.run(app, port=5000)
```

See [blog post](https://explodinglabs.github.io/jsonrpc/flask-socketio).

## Tornado

```python
from typing import Awaitable, Optional

from tornado import ioloop, web

from jsonrpcserver import Result, Success, async_dispatch, method


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


class MainHandler(web.RequestHandler):
    """Handle Tornado request"""

    async def post(self) -> None:
        """Post"""
        request = self.request.body.decode()
        response = await async_dispatch(request)
        if response:
            self.write(response)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass


app = web.Application([(r"/", MainHandler)])

if __name__ == "__main__":
    app.listen(5000)
    ioloop.IOLoop.current().start()
```

See [blog post](https://explodinglabs.github.io/jsonrpc/tornado).

## Websockets

```python
import asyncio

from websockets.server import WebSocketServerProtocol, serve

from jsonrpcserver import Result, Success, async_dispatch, method


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


async def main(websocket: WebSocketServerProtocol, _: str) -> None:
    """Handle Websocket message"""
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = serve(main, "localhost", 5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

See [blog post](https://explodinglabs.github.io/jsonrpc/websockets).

## Werkzeug

```python
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from jsonrpcserver import Result, Success, dispatch, method


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@Request.application
def application(request: Request) -> Response:
    """Handle Werkzeug request"""
    return Response(dispatch(request.data.decode()), 200, mimetype="application/json")


if __name__ == "__main__":
    run_simple("localhost", 5000, application)
```

See [blog post](https://explodinglabs.github.io/jsonrpc/werkzeug).

## ZeroMQ

```python
import zmq

from jsonrpcserver import Result, Success, dispatch, method

socket = zmq.Context().socket(zmq.REP)


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


if __name__ == "__main__":
    socket.bind("tcp://*:5000")
    while True:
        request = socket.recv().decode()
        socket.send_string(dispatch(request))
```

See [blog post](https://explodinglabs.github.io/jsonrpc/zeromq).

## ZeroMQ (async)

```python
import asyncio

import aiozmq  # type: ignore
import zmq

from jsonrpcserver import Result, Success, async_dispatch, method


@method
async def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


async def main() -> None:
    """Handle AioZMQ request"""
    rep = await aiozmq.create_zmq_stream(zmq.REP, bind="tcp://*:5000")
    while True:
        request = (await rep.read())[0].decode()
        if response := (await async_dispatch(request)).encode():
            rep.write((response,))


if __name__ == "__main__":
    asyncio.set_event_loop_policy(aiozmq.ZmqEventLoopPolicy())
    asyncio.get_event_loop().run_until_complete(main())
```

See [blog post](https://explodinglabs.github.io/jsonrpc/zeromq-async).
