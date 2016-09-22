from flask import Flask, request, Response
from jsonrpcserver import Methods, dispatch

methods = Methods()
@methods.add
def ping():
    return 'pong'

app = Flask(__name__)
@app.route('/', methods=['POST'])
def index():
    r = dispatch(methods, request.get_data().decode())
    return Response(str(r), r.http_status, mimetype='application/json')

if __name__ == '__main__':
    app.run()
