from jsonrpcserver import method, serve, Ok, Result


@method
def ping() -> Result:
    return Ok("pong")


if __name__ == "__main__":
    serve()
