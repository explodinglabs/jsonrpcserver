from django.http import HttpRequest, HttpResponse  # type: ignore
from django.views.decorators.csrf import csrf_exempt  # type: ignore
from jsonrpcserver import method, Result, Success, dispatch


@method
def ping() -> Result:
    return Success("pong")


@csrf_exempt  # type: ignore
def jsonrpc(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
