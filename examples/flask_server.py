from flask import Flask, Response, request
from jsonrpcserver import method, Result, Success, dispatch

app = Flask(__name__)


@method
def ping() -> Result:
    return Success("pong")


@app.route("/", methods=["POST"])
def index():
    print(request.get_data().decode())
    return Response(
        dispatch(request.get_data().decode()), content_type="application/json"
    )


if __name__ == "__main__":
    app.run()
