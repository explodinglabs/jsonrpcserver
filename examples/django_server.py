from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import method, dispatch


@method
def ping():
    return "pong"


@csrf_exempt
def jsonrpc(request):
    response = dispatch(request.body.decode())
    return JsonResponse(
        response.deserialized(), status=response.http_status, safe=False
    )
