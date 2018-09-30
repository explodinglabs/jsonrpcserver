from flask import Flask
from flask_socketio import SocketIO, send
from jsonrpcserver import method, dispatch

app = Flask(__name__)
socketio = SocketIO(app)

@method
def ping():
    return 'pong'

@socketio.on('message')
def handle_message(request):
    response = dispatch(request)
    if response.wanted:
        send(response, json=True)

if __name__ == '__main__':
    socketio.run(app, port=5000)
