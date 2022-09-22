from flask import Flask, Request
from flask_socketio import SocketIO, send  # type: ignore
from jsonrpcserver import method, Result, Success, dispatch

app = Flask(__name__)
socketio = SocketIO(app)


@method
def ping() -> Result:
    return Success("pong")


@socketio.on("message")  # type: ignore
def handle_message(request: Request) -> None:
    if response := dispatch(request):
        send(response, json=True)


if __name__ == "__main__":
    socketio.run(app, port=5000)
