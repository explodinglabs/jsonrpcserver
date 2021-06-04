from flask import Flask, request
from jsonrpcserver import method, dispatch
from jsonrpcserver.result import Result, Success
from jsonrpcserver.response import to_json

app = Flask(__name__)


@method
def ping() -> Result:
    return Success("pong")


@app.route("/", methods=["POST"])
def index() -> str:
    return to_json(dispatch(request.get_data().decode()))


if __name__ == "__main__":
    app.run()
