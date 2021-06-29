from flask import Flask, request  # type: ignore
from jsonrpcserver import method, dispatch, Result, Success

app = Flask(__name__)


@method
def ping() -> Result:
    return Success("pong")


@app.route("/", methods=["POST"])
def index() -> str:
    return dispatch(request.get_data().decode())


if __name__ == "__main__":
    app.run()
