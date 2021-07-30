"""Using jsonrpcserver's built-in serve() function"""
from jsonrpcserver import Success, method, serve


@method
def ping():
    return Success("pong")


if __name__ == "__main__":
    serve()
