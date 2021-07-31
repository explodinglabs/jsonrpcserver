from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import method, dispatch


@method
def ping():
    return "pong"


@csrf_exempt
def jsonrpc(request):
    return HttpResponse(
        dispatch(request.body.decode()), content_type="application/json"
    )
