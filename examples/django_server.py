from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import dispatch, method, Ok, Result


@method
def ping() -> Result:
    return Ok("pong")


@csrf_exempt
def jsonrpc(request):
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
