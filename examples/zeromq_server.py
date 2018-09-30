import zmq
from jsonrpcserver import method, dispatch

socket = zmq.Context().socket(zmq.REP)

@method
def ping():
    return 'pong'

if __name__ == '__main__':
    socket.bind('tcp://*:5000')
    while True:
        request = socket.recv().decode()
        response = dispatch(request)
        socket.send_string(str(response))
