"""run.py

An example app, demonstrating how to use the jsonrpcserver library.
"""

from flask import Flask, request

from jsonrpcserver import bp, dispatch, exceptions


# Create a Flask app and register the blueprint.
app = Flask(__name__)
app.register_blueprint(bp)


# Write the methods that will carry out the JSON-RPC requests.
class HandleRequests:
    """Methods to handle each JSON-RPC request."""

    @staticmethod
    def add(x, y):
        """Add two numbers."""
        try:
            return x + y
        except TypeError:
            raise exceptions.InvalidParams('Type error')


# Add a route to pass requests on to your methods
@app.route('/', methods=['POST'])
def index():
    """Dispatch requests to the handling methods."""
    return dispatch(request.get_json(), HandleRequests)


if __name__ == '__main__':
    app.run()
