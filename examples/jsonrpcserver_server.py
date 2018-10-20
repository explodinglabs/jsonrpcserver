"""Using jsonrpcserver's built-in serve() function"""
from jsonrpcserver import method, serve


@method
def ping():
    return "pong"


if __name__ == "__main__":
    serve()
