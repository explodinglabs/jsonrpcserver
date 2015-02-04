"""run.py

An example app, demonstrating how to use the jsonrpcserver library.
"""

from flask import Flask, request

from jsonrpcserver import bp, dispatch, exceptions


# Create a Flask app and register the blueprint.
app = Flask(__name__)
app.register_blueprint(bp)

# Add a route to take requests.
@app.route('/', methods=['POST'])
def index():
    """Dispatch requests to the handling methods."""
    return dispatch(request.get_json(), HandleRequests)


# Write the methods that will carry out the requests.
class HandleRequests:
    """Methods to handle each request."""

    @staticmethod
    def add(x, y):
        """Add two numbers."""
        try:
            return x + y
        except TypeError:
            raise exceptions.InvalidParams('Type error')


if __name__ == '__main__':
    app.run()
