from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import methods

@methods.add
def ping():
    return 'pong'

@csrf_exempt
def jsonrpc(request):
    response = methods.dispatch(request.body.decode())
    return JsonResponse(response, status=response.http_status)
