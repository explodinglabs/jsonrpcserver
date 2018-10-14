from flask import Flask, request, Response
from jsonrpcserver import method, dispatch

app = Flask(__name__)


@method
def ping():
    return "pong"


@app.route("/", methods=["POST"])
def index():
    req = request.get_data().decode()
    response = dispatch(req)
    return Response(str(response), response.http_status, mimetype="application/json")


if __name__ == "__main__":
    app.run()
