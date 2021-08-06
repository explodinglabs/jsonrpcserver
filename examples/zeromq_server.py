from jsonrpcserver import method, Result, Success, dispatch
import zmq

socket = zmq.Context().socket(zmq.REP)


@method
def ping() -> Result:
    return Success("pong")


if __name__ == "__main__":
    socket.bind("tcp://*:5000")
    while True:
        request = socket.recv().decode()
        socket.send_string(dispatch(request))
