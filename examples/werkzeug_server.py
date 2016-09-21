from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpcserver import Methods, dispatch

methods = Methods()
@methods.add
def ping():
    return 'pong'

@Request.application
def application(request):
    r = dispatch(methods, request.data.decode())
    return Response(str(r), r.http_status, mimetype='application/json')

run_simple('localhost', 5000, application)
