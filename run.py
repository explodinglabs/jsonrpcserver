"""run.py

An example app, demonstrating how to use the library.
"""

import sys
from flask import Flask
from jsonrpcserver import bp, dispatch, exceptions

# Create flask app and register the blueprint.
app = Flask(__name__)
app.register_blueprint(bp)

# Make a route for client access, and dispatch.
@app.route('/', methods=['POST'])
def index():
    return dispatch(sys.modules[__name__])

# Write methods to carry out the requests.
def add(num1, num2='Not a number'):
    try:
        return num1 + num2
    except TypeError as e:
        raise exceptions.InvalidParams(str(e))

if __name__ == '__main__':
    app.run()
