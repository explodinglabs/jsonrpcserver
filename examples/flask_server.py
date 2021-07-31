from flask import Flask, Response, request  # type: ignore
from jsonrpcserver import Result, Success, dispatch, method

app = Flask(__name__)


@method
def ping() -> Result:
    return Success("pong")


@app.route("/", methods=["POST"])
def index() -> str:
    return Response(
        dispatch(request.get_data().decode()), content_type="application/json"
    )


if __name__ == "__main__":
    app.run()
