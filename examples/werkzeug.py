from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpcserver import method, dispatch


@method
def ping():
    return "pong"


@Request.application
def application(request):
    response = dispatch(request.data.decode())
    return Response(str(response), response.http_status, mimetype="application/json")


if __name__ == "__main__":
    run_simple("localhost", 5000, application)
