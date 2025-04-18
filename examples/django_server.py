"""Django server"""
from django.http import HttpRequest, HttpResponse  # type: ignore
from django.views.decorators.csrf import csrf_exempt  # type: ignore

from jsonrpcserver import Result, Success, dispatch, method


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Success("pong")


@csrf_exempt  # type: ignore
def jsonrpc(request: HttpRequest) -> HttpResponse:
    """Handle Django request"""
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
