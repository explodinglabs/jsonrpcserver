"""flask-example.py

Demonstrates the jsonrpcserver library in a Flask app.

Install::

    $ pip install flask jsonrpcserver

Run::

    $ python flask-example.py
"""
from flask import Flask, request, jsonify
from jsonrpcserver import Dispatcher


# Create a Flask app and a Dispatcher.
app = Flask(__name__)
api = Dispatcher()


# Write the handling methods.
@api.method('add')
def add(x, y):
    """Add two numbers."""
    return x + y


# Add a route to take the requests and pass them on to your methods.
@app.route('/api', methods=['POST'])
def index():
    """The api route."""
    result, status = api.dispatch(request.get_json())
    return jsonify(result) if result else '', status


if __name__ == '__main__':
    app.run()
