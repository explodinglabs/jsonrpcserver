"""Werkzeug server"""
from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response

from jsonrpcserver import Result, Success, dispatch, method


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@Request.application
def application(request: Request) -> Response:
    """Handle Werkzeug request"""
    return Response(dispatch(request.data.decode()), 200, mimetype="application/json")


if __name__ == "__main__":
    run_simple("localhost", 5000, application)
