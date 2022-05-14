from flask import Flask
from flask_socketio import SocketIO, send
from jsonrpcserver import dispatch, method, Ok, Result

app = Flask(__name__)
socketio = SocketIO(app)


@method
def ping() -> Result:
    return Ok("pong")


@socketio.on("message")
def handle_message(request):
    if response := dispatch(request):
        send(response, json=True)


if __name__ == "__main__":
    socketio.run(app, port=5000)
