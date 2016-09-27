from flask import Flask, request, Response
from jsonrpcserver import methods

app = Flask(__name__)

@methods.add
def ping():
    return 'pong'

@app.route('/', methods=['POST'])
def index():
    response = methods.dispatch(request.get_data().decode())
    return Response(str(response), response.http_status,
                    mimetype='application/json')

if __name__ == '__main__':
    app.run()
