import zmq
from jsonrpcserver import Success, method, dispatch

socket = zmq.Context().socket(zmq.REP)


@method
def ping():
    return Success("pong")


if __name__ == "__main__":
    socket.bind("tcp://*:5000")
    while True:
        request = socket.recv().decode()
        socket.send_string(dispatch(request))
