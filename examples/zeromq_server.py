"""ZeroMQ server"""
import zmq
from jsonrpcserver import dispatch, method, Ok, Result

socket = zmq.Context().socket(zmq.REP)


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


if __name__ == "__main__":
    socket.bind("tcp://*:5000")
    while True:
        request = socket.recv().decode()
        socket.send_string(dispatch(request))
