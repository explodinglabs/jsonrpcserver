from flask import Flask
from flask_socketio import SocketIO, send
from jsonrpcserver import methods
from jsonrpcserver.response import NotificationResponse

app = Flask(__name__)
socketio = SocketIO(app)

@methods.add
def ping():
    return 'pong'

@socketio.on('message')
def handle_message(request):
    response = methods.dispatch(request)
    if not response.is_notification:
        send(response, json=True)

if __name__ == '__main__':
    socketio.run(app, port=5000)
