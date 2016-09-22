import zmq
from jsonrpcserver import Methods, dispatch

methods = Methods()
@methods.add
def ping():
    return 'pong'

context = zmq.Context()
socket = context.socket(zmq.REP)

if __name__ == '__main__':
    socket.bind('tcp://*:5000')
    while True:
        request = socket.recv().decode()
        response = dispatch(methods, request)
        socket.send_string(str(response))
