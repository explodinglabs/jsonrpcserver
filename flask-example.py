"""flask-example.py

A simple server demonstrating the jsonrpcserver library in a Flask environment.

To run it::
    $ pip install flask
    $ python flask-example.py

Then with a client, post a request::
    $ curl -X POST -H 'Content-type: application/json' \
    > -d '{"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1}' \
    > http://localhost:5000/api
    {
        "jsonrpc": "2.0",
        "result": 3,
        "id": 1
    }
"""

from flask import Flask, request, jsonify

from jsonrpcserver import Dispatcher
from jsonrpcserver.exceptions import InvalidParams


# Create a Flask app and a Dispatcher.
app = Flask(__name__)
api = Dispatcher()


# Write the handling methods.
@api.method('add')
def add(x, y):
    """Add two numbers."""
    try:
        return x + y
    except TypeError:
        raise InvalidParams('Type error')


# Add a route to take the requests and pass them on to your methods.
@app.route('/api', methods=['POST'])
def index():
    """The api route."""
    result, status = api.dispatch(request.get_json())
    return jsonify(result) if result else '', status


if __name__ == '__main__':
    app.run()
