"""example.py

A simple server that returns the sum of two numbers.

To run it::

    $ python run.py

Then with a client, post a request::

    $ curl -X POST -H 'Content-type: application/json' \
    > -d '{"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1}' \
    > http://localhost:5000/
    {
        "jsonrpc": "2.0",
        "result": 3,
        "id": 1
    }
"""

from flask import Flask, request

from jsonrpcserver import bp, dispatch
from jsonrpcserver.exceptions import InvalidParams


# Create a Flask app and register the blueprint to it.
app = Flask(__name__)
app.register_blueprint(bp)


# Write the handling methods.
def add(x, y):
    """Add two numbers."""
    try:
        return x + y
    except TypeError:
        raise InvalidParams('Type error')


# Add a route to take the requests and pass them on to your methods.
@app.route('/', methods=['POST'])
def index():
    """The json-rpc route."""
    return dispatch(request.get_json())


if __name__ == '__main__':
    app.run()
