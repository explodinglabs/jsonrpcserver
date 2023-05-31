"""Django server"""
from django.http import HttpRequest, HttpResponse  # type: ignore
from django.views.decorators.csrf import csrf_exempt  # type: ignore
from jsonrpcserver import dispatch, method, Ok, Result


@method
def ping() -> Result:
    """JSON-RPC method"""
    return Ok("pong")


@csrf_exempt  # type: ignore
def jsonrpc(request: HttpRequest) -> HttpResponse:
    """Handle Django request"""
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
